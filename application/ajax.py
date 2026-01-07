from flask import Blueprint, Response, url_for, render_template, send_from_directory, send_file, stream_with_context, abort, jsonify, make_response, request, current_app
from jinja2.exceptions import TemplateNotFound
import json
import numpy as np
import pandas as pd
from typing import cast

from . import AppContext
from .custom.db.user.models import Template
from .custom.utils.mdpdf import MdPDF



# Cast app_context typing
app = cast(AppContext, current_app)
# Create blueprint
ajax = Blueprint('ajax', __name__)




@ajax.route('/tabs/<section_id>/<tab_id>', methods=['GET'])
def load_tab(section_id, tab_id):
    try:
        tab = render_template(f"{section_id}/{tab_id}.html")
        return tab
    except TemplateNotFound:
        abort(404)


# --------------------
# POPUPS

@ajax.route('/upload_file_popup/<title>', methods=['GET'])
def upload_file_popup(title:str):
    popup = render_template('elements/upload_file_popup.html', title=title)
    return popup

@ajax.route('/create_file_popup/<title>', methods=['GET'])
def create_file_popup(title:str):
    popup = render_template('elements/create_file_popup.html', title=title)
    return popup

@ajax.route('/attach_template_popup/<category>', methods=['GET'])
def attach_resume_popup(category:str):
    templates = app.user_db.get_templates()
    c_template = [template.dict() for template in templates if template.category == category]
    popup = render_template('elements/attach_template_popup.html', templates=c_template, category=category)
    return popup

@ajax.route('/model_settings_popup', methods=['GET'])
def model_settings_popup():
    inputs = [{'name': key, 'value': value} for key, value in request.args.items()]
    popup = render_template('elements/model_settings_popup.html', settings=inputs)
    return popup

@ajax.route('offer_fullview_popup/<offer_id>', methods=['GET'])
def offer_fullview_popup(offer_id:str):
    (offer,), (id,) = app.offer_db.get_offers(ids=[offer_id])
    (cluster,), _ = app.offer_db.get_clusters(id=id)
    #  TODO: pass offer.url as offer_url
    return offer.render(id, style='fullview', category=cluster.name)


# --------------------
# TEMPLATES

@ajax.route('/get_templates', methods=['GET'])
def get_templates():
    templates = app.user_db.get_templates()
    response = {}
    for t in templates:
        if not response.get(t.category):
            response[t.category] = []
        response[t.category].append(t.render_html())
    return jsonify(response)

@ajax.route('/create_template', methods=['POST'])
def create_template():
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')

    match category:
        case 'resume':
            file = request.files.get('file')
            uuid, path = app.data.create_resume_template(file)
        case 'coverletter':
            uuid, path = app.data.create_coverletter_template()
        case 'email':
            uuid, path = app.data.create_email_template()
        case _:
            raise Exception(f'Unknowned category "{category}"')
    
    template = Template(uuid=uuid, title=name, description=description, category=category, path=path)
    app.user_db.create_template(template)

    return jsonify({"category": template.category, "uuid": template.uuid, "html": template.render_html()})

@ajax.route('/templates/<path:filename>')
def serve_template_file(filename):
    return send_from_directory('../data', filename)

@ajax.route('/read_template/<template_uuid>')
def read_template(template_uuid:str):
    template = app.user_db.get_template(template_uuid)
    if template.category == 'resume':
        content = url_for('ajax.serve_template_file', filename=template.path)
    else:
        content = app.data.read(template.path) 
    return jsonify({'category': template.category, 'content': content})

@ajax.route('/update_template/<template_uuid>', methods=['PUT'])
def update_template(template_uuid:str):
    content = request.json.get('content')
    template = app.user_db.get_template(template_uuid)
    app.data.update(template.path, content)
    return jsonify({'success': True})

@ajax.route('/delete_template/<template_uuid>', methods=['DELETE'])
def delete_template(template_uuid:str):
    with app.user_db.connect() as conn:
        template = app.user_db.remove_template(conn, template_uuid)
        app.data.delete(template.path)
    return jsonify({'success': True})

@ajax.route('/generate_template')
def generate_template():
    email = request.args.get('email')
    coverletter = request.args.get('coverletter')
    offer_id = request.args.get('offer_id')
    if not any([email, coverletter]):
        print('no template')
        return abort(422, "Missing template uuid. Use `email` or `coverletter` param to send a template uuid")
    if not offer_id:
        print('no offer_id')
        return abort(422, "Missing `offer_id` param")
    
    # TODO: generate email or template base on offer description

    template_content = "Ceci sera ma template"
    return jsonify({'template': template_content})

# --------------------
# DATA

@ajax.route('/bdd_info/<source>')
def bdd_info(source:str):
    if source not in {'NTNE', 'APEC'}:
        abort(404, description='Invalid source')

    total = app.offer_db.get_total(source=source)
    latest_date = app.offer_db.get_latest_date(source=source, isostring=True)
    rows = app.offer_db.summary(source=source)
    
    return jsonify({
        'total': total,
        'date': latest_date or 'NA',
        'summary': rows
    })

@ajax.route('/update_bdd_stream/<source>')
def update_bdd_stream(source: str):
    if source not in {'NTNE', 'APEC'}:
        abort(404, description='Invalid source')

    
    def event_stream():
        db_total = app.offer_db.get_total(source=source)
        latest_date = app.offer_db.get_latest_date(source=source)

        if source == 'NTNE':
            api_total = app.ntne_api.get_total()
            iterator = app.ntne_api.iter_search(stop_date=latest_date)
        else:
            api_total = app.apec_api.get_total()
            iterator = app.apec_api.iter_search(stop_date=latest_date)

        total = 0
        step = 1 / (api_total - db_total)
        offers = []

        try:
            for offer in iterator:
                offers.append(offer)
                total += 1
                yield f"data: {json.dumps({'count': total, 'progress': total*step*100})}\n\n"

            # Add remaining batch
            if offers:
                app.offer_db.add_offers(offers)

            db_total = app.offer_db.get_total(source=source)
            yield "event: end\ndata: complete\n\n"

        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
            raise

    headers = {
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',  # disable buffering if behind nginx
    }
    return Response(stream_with_context(event_stream()),
                    mimetype='text/event-stream',
                    headers=headers)

@ajax.route('process_nlp/<source>')
def process_nlp(source:str):
    if source not in {'NTNE', 'APEC'}:
        abort(404, description='Invalid source')

    ids, descriptions = app.offer_db.get_unprocessed(source)
    if not ids:
        return jsonify({"success": True})
    
    emb_50d, emb_3d = app.nlp.tfidf.transform(descriptions, save=True)
    labels, clusters = app.nlp.kmeans.predict(emb_50d)

    with app.offer_db.connect() as conn:
        for id, emb50, emb3, cluster_id in zip(ids, emb_50d, emb_3d, labels):
            for cluster in clusters:
                if cluster.id == cluster_id:
                    c = cluster
                    break
            app.offer_db.add_nlp(conn, id, emb_50d=emb50, emb_3d=emb3, cluster=c)
        conn.commit()

    return jsonify({"success": True})


@ajax.route('fit_kmeans', methods=['POST'])
def fit_kmeans():
    K = int(request.form.get('K'))
    if not K:
        abort(400, 'Missing required parameter "K"')

    with app.offer_db.connect() as conn:
        emb, offer_ids = app.offer_db.get_embeddings(conn)
        emb_50d = [e.d50 for e in emb]
    X, tokens = app.nlp.tfidf.load_matrix()
    labels, clusters = app.nlp.kmeans.fit_predict(X, emb_50d, tokens, K=K)

    # Create cluster names
    template = [{
        'cluster_id': c.id,
        'main_tokens': c.main_tokens,
        'cluster_name': None
    } for c in clusters]
    response = app.nlp.llm.request_json(
        "Je fais du clustering d'offres d'emploi dans la data. Je me base sur les descriptions des offres. Trouve des noms pour mes clusters selon les tokens principaux.",
        json_template=template
    )
    for c in response:
        cluster_id = c['cluster_id']
        clusters[cluster_id].name = c['cluster_name']

    # Save data
    with app.offer_db.connect() as conn:
        app.offer_db.clear_table(conn, 'CLUSTER')
        for offer_id, cluster_id in zip(offer_ids, labels):
            c = clusters[cluster_id]
            app.offer_db.add_nlp(conn, offer_id, cluster=c)

    return jsonify(app.nlp.kmeans.metadata)

@ajax.route('fit_tfidf', methods=['POST'])
def fit_tfidf():
    min_df = int(request.form.get('min_df'))
    max_df = float(request.form.get('max_df'))
    if not all([min_df, max_df]):
        abort(400, 'Missing required parameter "min_df" and / or "max_df"')
        
    offers, ids = app.offer_db.get_offers()
    descriptions = [offer.description.offer_description for offer in offers]
    emb_50d, emb_3d = app.nlp.tfidf.fit_transform(descriptions, min_df=min_df, max_df=max_df)

    with app.offer_db.connect() as conn:
        app.offer_db.clear_table(conn, 'TFIDF')
        for offer_id, emb50, emb3 in zip(ids, emb_50d, emb_3d):
            app.offer_db.add_nlp(conn, offer_id, emb_50d=emb50, emb_3d=emb3)

    return jsonify(app.nlp.tfidf.metadata)


@ajax.route('get_models_metadata')
def get_models_metadata():
    models = {
        'kmeans': app.nlp.kmeans.metadata,
        'tfidf': app.nlp.tfidf.metadata
    }
    return jsonify(models)



# --------------------
# OFFERS

@ajax.route('render_offers')
def render_offers():
    ids = request.args.getlist('id', type=int)
    offers, ids = app.offer_db.get_offers(ids=ids)
    offer_htmls = [offer.render(id, style='preview') for offer, id in zip(offers, ids)]
    return jsonify(offer_htmls)

@ajax.route('get_offers')
def get_offers():
    offers = app.offer_db.get_table('OFFER', columns=['offer_id', 'title', 'salary_min', 'latitude', 'longitude'])
    return jsonify({'count': len(offers), 'offers': offers.dict})

@ajax.route('get_saved_offers')
def get_saved_offers():
    ids = app.user_db.get_saved_offers()
    return jsonify(ids)

@ajax.route('get_applied_offers')
def get_applied_offers():
    ids = app.user_db.get_applied_offers()
    return jsonify(ids)

@ajax.route('save_offer/<id>', methods=['POST'])
def save_offer(id:str):
    app.user_db.save_offer(id)
    return jsonify({'success': True})

@ajax.route('unsave_offer/<id>', methods=['DELETE'])
def unsave_offer(id:str):
    app.user_db.unsave_offer(id)
    return jsonify({'success': True})

@ajax.route('mark_offer_as_apply/<offer_id>', methods=['POST'])
def mark_offer_as_apply(offer_id:str):
    app.user_db.apply_offer(offer_id)
    return jsonify({'success': True})

@ajax.route('/select_offers', methods=['POST'])
def select_offers():
    ids = request.get_json()
    offers, ids = app.offer_db.get_offers(ids=ids)
    offer_htmls = [offer.render(id, style='preview') for offer, id in zip(offers, ids)]
    return jsonify(offer_htmls)

@ajax.route('/search_offer')
def search_offer():
    query = None
    resume = None
    filters = []
    far = []
    near = []

    # create query embeddings
    if request.args.get('query'):
        emb_50d, _ = app.nlp.tfidf.transform([request.args.get('query')])
        query = emb_50d
    # create filters
    for key in ['salary', 'category', 'company', 'city']:
        if request.args.get(key):
            filters.append({key: request.args.get(key)})
    # create resume embeddings
    if request.args.get('resume'):
        template = app.user_db.get_template(request.args.get('resume'))
        template_text = app.data.read(template.path, pdf=True)
        emb_50d, _ = app.nlp.tfidf.transform([template_text])
        resume = emb_50d
        if not query:
            query = emb_50d # If no query provided, resume content become query
            
    # create refines (like and dislikes)
    if request.args.get('refine'):
        with app.offer_db.connect() as conn:
            for refine in json.loads(request.args.get('refine')):
                offer_id = refine['offer_id']
                emb, _ = app.offer_db.get_embeddings(conn, offer_id)
                match refine['type']:
                    case 'like':
                        near.append(emb.d50)
                    case 'dislike':
                        far.append(emb.d50)
    # get render style
    style = request.args.get('style')

    # adjust query based on refines
    if near:
        mean_near = np.mean(np.stack(near, axis=0), axis=0)
        query = query + (0.5 * mean_near)
    if far:
        mean_far = np.mean(np.stack(far, axis=0), axis=0)
        query = query - (0.5 * mean_far)
    if any([near, far]):
        # normalize the query if has been adjusted (divide by its L2 norm)
        query = query / np.linalg.norm(query)

    offers, ids, scores = app.offer_db.search_offer(query=query, resume=resume, filters=filters)

    offers_html = [offer.render(id_, score=score, style=style) for offer, id_, score in zip(offers, ids, scores)]
    offers_data = [offer.dict() for offer in offers]

    return jsonify({'html': offers_html, 'data': offers_data})




# --------------------
# PLOTS


@ajax.route('/cluster_plot')
def cluster_plot():
    with app.offer_db.connect() as conn:
        # Get embeddings
        emb, offer_ids = app.offer_db.get_embeddings(conn)
        offers = pd.DataFrame({
            'offer_id': offer_ids,
            'emb_50d': [e.d50 for e in emb],
            'emb_3d': [e.d3 for e in emb]
        })
        # Get clusters
        clusters, offer_ids = app.offer_db.get_clusters(conn=conn)
        cluster_map = dict(zip(offer_ids, clusters))  # clusters_offer_ids from get_clusters
        offers['cluster'] = offers['offer_id'].map(cluster_map)
        # Get offer titles
        titles = app.offer_db.get_table('OFFER', columns=['title'], conn=conn)
        title_map = dict(zip(titles.rowids, titles.rows))
        offers['title'] = offers['offer_id'].map(title_map)


    # Render cluster htmls
    fig_dict = app.plot.clusters.render(
        offers['emb_3d'].tolist(), 
        offers['cluster'].tolist(), 
        offers['title'].tolist(), 
        ids=offers['offer_id'].tolist()
    )
    return jsonify(fig_dict)

@ajax.route('stat_plots')
def stat_plots():
    data = app.offer_db.get_table('OFFER', columns=['job_name', 'contract_type'])
    # Split data
    job_names = []
    contracts = []
    for d in data.dict:
        job_names.append(d.get('job_name'))
        contracts.append(d.get('contract_type'))
    # Render plots
    job_fig = app.plot.job_fig.render(job_names)
    contract_fig = app.plot.contract_fig.render(contracts)
    return jsonify({
        'topJobs': job_fig, 
        'contracts': contract_fig
    })



# --------------------
# APPLY

@ajax.route('apply_offer/<offer_id>')
def apply_offer(offer_id:str):
    email = request.args.get('email')
    coverletter = request.args.get('coverletter')

    # Create response
    response = make_response(jsonify({'success': True}), 200)
    response.headers['X-Is-File'] = 'no'

    # Create templates
    if email:
        email_id, _ = app.data.create_email_template(content=email)
    if coverletter:
        coverletter_id, _ = app.data.create_coverletter_template(content=coverletter)
        pdf_buffer = MdPDF.pdf_from_md(coverletter)
        response = make_response(
            send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='Lettre de motivation.pdf'
            )
        )
        response.headers['X-Is-File'] = 'yes'
        
    return response