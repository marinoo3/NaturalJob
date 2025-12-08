from datetime import datetime
from ..objects import Template




class FileTable:

    def create_template(self, uuid, title, description, category, path) -> Template:

        # TODO: add the document to database

        date = datetime.now().strftime('%d/%m/%Y')
        template = Template(uuid, title, description, category, date, path)
        return template
    
    def get_templates(self):

        # TODO: get the list of templates and there info from database
        dummy = Template(
            '15327e9f-2548-4b6f-9a0d-7e69ca34ecdf', 
            'CV - Marin NAGY', 
            'Version orienté Computer Vision', 
            'resume', 
            '21/10/2025', 
            'usr/resume/15327e9f-2548-4b6f-9a0d-7e69ca34ecdf.pdf')
        return [dummy]