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
            yield f"data: {json.dumps({'status': 'done'})}\n\n"
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



# TEST
@ajax.route('/serve_pdf')
def serve_pdf():
    return send_from_directory('../data/usr/resume/', '03f85020-1dc6-4ac5-a33d-d7727fb4f08e.pdf')