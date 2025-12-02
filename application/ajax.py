from flask import Blueprint, render_template, abort, jsonify
from jinja2.exceptions import TemplateNotFound



ajax = Blueprint('ajax', __name__)




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