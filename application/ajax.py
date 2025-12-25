from flask import Blueprint, Response, url_for, render_template, send_from_directory, stream_with_context, abort, jsonify, request, current_app
from jinja2.exceptions import TemplateNotFound
import json
from typing import cast

from . import AppContext
from .custom.db.user.models import Template


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
                app.offer_db.add(offers)

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

    def event_stream():
        try:
            ids, descriptions = app.offer_db.get_unprocessed(source)
            if not ids:
                yield "event: end\ndata: complete\n\n"
                return
            
            yield "event: progress\ndata: Traitement des données\n\n"
            
            emb_50d, emb_3d = app.nlp.tfidf.transform(descriptions)
            labels, clusters = app.nlp.kmeans.predict(emb_50d)

            with app.offer_db.connect() as conn:
                for id, emb50, emb3, cluster_id in zip(ids, emb_50d, emb_3d, labels):
                    c = clusters[cluster_id]
                    app.offer_db.add_nlp(conn, id, emb_50d=emb50, emb_3d=emb3, cluster=c)
                conn.commit()

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

@ajax.route('fit_kmeans', methods=['POST'])
def fit_kmeans():
    K = request.form.get('K')
    K = 5
    if not K:
        abort(400, 'Missing required parameter "K"')

    ids = app.offer_db.get_table('OFFER', columns=['offer_id'])
    emb_50ds = app.offer_db.get_table('TFIDF', columns=['emb_50d'], convert_blob=True)
    X, tokens = app.nlp.tfidf.load_matrix()
    labels, clusters = app.nlp.kmeans.fit_predict(X, emb_50ds, tokens, K=K)

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
        for id, cluster_id in zip(ids, labels):
            c = clusters[cluster_id]
            app.offer_db.add_nlp(conn, id, cluster=c)

    return jsonify({'success': True})

@ajax.route('fit_tfidf', methods=['POST'])
def fit_tfidf():
    offers, ids = app.offer_db.search_offer()
    descriptions = [offer.description.offer_description for offer in offers]
    emb_50d, emb_3d = app.nlp.tfidf.fit_transform(descriptions)

    with app.offer_db.connect() as conn:
        app.offer_db.clear_table(conn, 'TFIDF')
        for offer_id, emb50, emb3 in zip(ids, emb_50d, emb_3d):
            app.offer_db.add_nlp(conn, offer_id, emb_50d=emb50, emb_3d=emb3)

    return jsonify({'success': True})

@ajax.route('/get_offers')
def get_offers():
    offers, _ = app.offer_db.search_offer()
    return jsonify({'count': len(offers), 'offers': [offer.dict() for offer in offers]})



# --------------------
# PLOTS


@ajax.route('/cluster_plot')
def cluster_plot():
    emb_3d = app.offer_db.get_table('TFIDF', columns=['emb_3d'], convert_blob=True)
    clusters, titles = app.offer_db.search_clusters()
    fig_dict = app.plot.clusters.render(emb_3d, clusters, titles)
    return jsonify(fig_dict)