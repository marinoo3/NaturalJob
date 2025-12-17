import sqlite3
from datetime import date
import os

from .models import Template




class UserDB():

    path = 'db/user.db'

    def __init__(self) -> None:
        root = os.environ.get('DATA_PATH', 'data/')
        self.db_path = os.path.join(root, self.path)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def create_template(self, template:Template) -> None:
        """Create a template object in DB
        
        Args:
            conn (sqlite3.Connection): a connection to the database
            uuid (str): the UUID of the new template object
            title (str): the title of the template
            description (str): the description of the template
            category (str): the category of the template
            path (str): the path of the template

        Return
            (Template): the created template oject
        """

        with self.connect() as conn:
            conn.execute("""
                INSERT INTO USER_FILE (ID, Title, Description, Category, Path, Date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, template.values())
    
    def get_templates(self) -> list[Template]:
        """Get all user template from DB
        
        Args:
            conn (sqlite3.Connection): a connection to the database

        Return
            (list[Template]): the list of user templates
        """
        with self.connect() as conn:
            cursor = conn.execute("""
                SELECT ID, Title, Description, Category, Path, Date FROM USER_FILE
            """)
            rows = cursor.fetchall()

        return [Template(*row) for row in rows]
    
    def get_template(self, uuid:str) -> Template:
        """Get a specific template from DB
        
        Args:
            conn (sqlite3.Connection): a connection to the database
            uuid (str): the UUID of the template to retrieve

        Return
            (Template): the template oject
        """
        with self.connect() as conn:
            row = conn.execute("""
                SELECT ID, Title, Description, Category, Path, Date
                    FROM USER_FILE
                    WHERE ID = ?
            """, (uuid,)).fetchone()
        return Template(*row) if row else None
    
    def remove_template(self, conn:sqlite3.Connection, uuid:str) -> Template:
        """Delete a specific template from DB
        
        Args:
            conn (sqlite3.Connection): a connection to the database
            uuid (str): the UUID of the template to delete

        Return
            (Template): the deleted template oject, if found
        """

        row = conn.execute("""
            SELECT ID, Title, Description, Category, Path, Date 
            FROM USER_FILE
            WHERE ID = ?
        """, (uuid,)).fetchone()

        if row is None:
            return None  # nothing to remove

        conn.execute("DELETE FROM USER_FILE WHERE ID = ?", (uuid,))

        return Template(*row)