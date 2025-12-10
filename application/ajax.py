from flask import Blueprint, url_for, render_template, send_from_directory, abort, jsonify, request, current_app
from jinja2.exceptions import TemplateNotFound


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

    templates = current_app.db.files.get_templates()
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

    # TODO: Use Transactions - Wrap database insert and file write in a transaction-like process, so I don’t end up with orphaned files or metadata if something fails.
    with current_app.db.files.connect() as conn:
        template = None
        match category:
            case 'resume':
                file = request.files.get('file')
                uuid, path = current_app.data.create_resume_template(file)
                template = current_app.db.files.create_template(conn, uuid, name, description, category, path)
            case 'coverletter':
                uuid, path = current_app.data.create_coverletter_template()
                template = current_app.db.files.create_template(conn, uuid, name, description, category, path)
            case 'email':
                uuid, path = current_app.data.create_email_template()
                template = current_app.db.files.create_template(conn, uuid, name, description, category, path)

        if not template:
            raise Exception(f'Unknowned category "{template}"')

    return jsonify({"category": template.category, "uuid": template.uuid, "html": template.render_html()})

@ajax.route('/templates/<path:filename>')
def serve_template_file(filename):
    return send_from_directory('data', filename)

@ajax.route('/read_template/<template_uuid>')
def read_template(template_uuid:str):
    template = current_app.db.files.get_template(template_uuid)
    if template.category == 'resume':
        content = url_for('ajax.serve_template_file', filename=template.path, _external=True)
    else:
        content = current_app.data.read(template.path) 
    return jsonify({'category': template.category, 'content': content})

@ajax.route('/update_template/<template_uuid>', methods=['PUT'])
def update_template(template_uuid:str):
    content = request.json.get('content')
    template = current_app.db.files.get_template(template_uuid)
    current_app.data.update(template.path, content)
    return jsonify({'success': True})

@ajax.route('/delete_template/<template_uuid>', methods=['DELETE'])
def delete_template(template_uuid:str):
    with current_app.db.files.connect() as conn:
        template = current_app.db.files.remove_template(conn, template_uuid)
        current_app.data.delete(template.path)
    return jsonify({'success': True})