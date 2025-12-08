from werkzeug.datastructures import FileStorage

import uuid
import os




class Data():

    resume = "usr/resume/"
    coverletter = "usr/coverletter/"
    email = "usr/email/"

    def __init__(self):
        self.path = os.environ.get('DATA_PATH', 'data/')
        self.__init_dir()

    def __init_dir(self):
        for relative_path in [self.resume, self.coverletter, self.email]:
            path = os.path.join(self.path, relative_path)
            os.makedirs(path, exist_ok=True)

    def create_resume_template(self, file: FileStorage):
        """Save resume template file to disk.

        Args:
            file (FileStorage): File to save as template (.pdf)

        Returns:
            template_id (str): the uuid of the created template
            relative_path (str): the relative path where the template is saved
        """

        # Generate unique identifier
        template_id = str(uuid.uuid4())
        # Save file to disk
        ext = file.filename.split('.')[-1]
        relative_path = os.path.join(self.resume, f'{template_id}.{ext}')
        file_path = os.path.join(self.path, relative_path)
        file.save(file_path)
        return template_id, relative_path
    
    def create_coverletter_template(self):
        """Create a cover letter template on disk.

        Returns:
            template_id (str): the uuid of the created template
            relative_path (str): the relative path where the template is saved
        """

        default = "# Template de lettre de motivation\n\nRédigez votre lettre au format `markdown`, elle sera adapaté automatiquement lors de la candidature a une offre"

        # Generate unique identifier
        template_id = str(uuid.uuid4())
        # Save file to disk
        relative_path = os.path.join(self.coverletter, f'{template_id}.md')
        file_path = os.path.join(self.path, relative_path)
        with open(file_path, 'w') as f:
            f.write(default)
        return template_id, relative_path, default
    
    def create_email_template(self):
        """Create an email template on disk.

        Returns:
            template_id (str): the uuid of the created template
            relative_path (str): the relative path where the template is saved
        """

        default = "# Template de mail\n\nRédigez une base de mail au format `markdown`, il sera personnalisé automatiquement lors de la candidature a une offre"

        # Generate unique identifier
        template_id = str(uuid.uuid4())
        # Save file to disk
        relative_path = os.path.join(self.email, f'{template_id}.md')
        file_path = os.path.join(self.path, relative_path)
        with open(file_path, 'w') as f:
            f.write(default)
        return template_id, relative_path, default