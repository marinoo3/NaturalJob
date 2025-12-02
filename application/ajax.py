from flask import Blueprint, render_template, abort, jsonify, request, current_app
from jinja2.exceptions import TemplateNotFound



ajax = Blueprint('ajax', __name__)


@ajax.route('/upload_file_popup/<title>', methods=['GET'])
def upload_file_popup(title):
    popup = render_template('elements/upload_file_popup.html', title=title)
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

    title = "CV - Marin NAGY"
    description = "Version orienté Computer Vision"
    date = "21/10/2025"
    id = "79863487821"

    template = render_template('elements/doc_template.html', title=title, description=description, date=date)

    return jsonify({"resume": [{"html": template, "id": id}]})

@ajax.route('/create_template', methods=['POST'])
def create_template():
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')

    # TODO: Use Transactions - Wrap database insert and file write in a transaction-like process, so I don’t end up with orphaned files or metadata if something fails.
    if category == 'resume':
        file = request.files.get('file')
        uuid, path = current_app.data.create_resume_template(file)
        current_app.db.create_template_record(uuid, name, description, category, path)
    if category == 'coverletter':
        uuid, path, content = current_app.data.create_coverletter_template()
        current_app.db.create_template_record(uuid, name, description, category, path)
    if category == 'email':
        uuid, path, content = current_app.data.create_email_template()
        current_app.db.create_template_record(uuid, name, description, category, path)

    return jsonify({"status": "success"})