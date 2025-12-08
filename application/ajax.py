from flask import Blueprint, render_template, abort, jsonify, request, current_app
from jinja2.exceptions import TemplateNotFound


ajax = Blueprint('ajax', __name__)


@ajax.route('/upload_file_popup/<title>', methods=['GET'])
def upload_file_popup(title):
    popup = render_template('elements/upload_file_popup.html', title=title)
    return popup

@ajax.route('/create_file_popup/<title>', methods=['GET'])
def create_file_popup(title):
    popup = render_template('elements/create_file_popup.html', title=title)
    return popup

@ajax.route('/tabs/<section_id>/<tab_id>', methods=['GET'])
def load_tab(section_id, tab_id):
    try:
        tab = render_template(f"{section_id}/{tab_id}.html")
        return tab
    except TemplateNotFound:
        abort(404)

@ajax.route('/get_templates', methods=['GET'])
def get_templates():

    templates = current_app.db.files.get_templates()
    response = {}
    for t in templates
    return jsonify(templates)

@ajax.route('/create_template', methods=['POST'])
def create_template():
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')

    # TODO: Use Transactions - Wrap database insert and file write in a transaction-like process, so I don’t end up with orphaned files or metadata if something fails.
    template = None
    match category:
        case 'resume':
            file = request.files.get('file')
            uuid, path = current_app.data.create_resume_template(file)
            template = current_app.db.files.create_template(uuid, name, description, category, path)
        case 'coverletter':
            uuid, path, content = current_app.data.create_coverletter_template()
            template = current_app.db.files.create_template(uuid, name, description, category, path)
        case 'email':
            uuid, path, content = current_app.data.create_email_template()
            template = current_app.db.files.create_template(uuid, name, description, category, path)

    if not template:
        raise Exception(f'Unknowned category "{template}"')

    return jsonify({"category": template.category, "html": template.render_html()})