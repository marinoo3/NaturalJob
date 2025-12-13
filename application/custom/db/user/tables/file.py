import sqlite3
from datetime import datetime

from ....objects import Template




class FileTable():

    def create_template(self, conn:sqlite3.Connection, uuid:str, title:str, description:str, category:str, path:str) -> Template:
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

        date = datetime.now().strftime('%d/%m/%Y')
        conn.execute("""
            INSERT INTO USER_FILE (ID, Title, Description, Category, Date, Path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uuid, title, description, category, date, path))
        return Template(uuid, title, description, category, date, path)
    
    def get_templates(self, conn:sqlite3.Connection) -> list[Template]:
        """Get all user template from DB
        
        Args:
            conn (sqlite3.Connection): a connection to the database

        Return
            (list[Template]): the list of user templates
        """

        cursor = conn.execute("""
            SELECT ID, Title, Description, Category, Date, Path FROM USER_FILE
        """)
        rows = cursor.fetchall()
        return [Template(*row) for row in rows]
    
    def get_template(self, conn:sqlite3.Connection, uuid:str) -> Template:
        """Get a specific template from DB
        
        Args:
            conn (sqlite3.Connection): a connection to the database
            uuid (str): the UUID of the template to retrieve

        Return
            (Template): the template oject
        """

        row = conn.execute("""
            SELECT ID, Title, Description, Category, Date, Path
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
            SELECT ID, Title, Description, Category, Date, Path
            FROM USER_FILE
            WHERE ID = ?
        """, (uuid,)).fetchone()

        if row is None:
            return None  # nothing to remove

        conn.execute("DELETE FROM USER_FILE WHERE ID = ?", (uuid,))

        return Template(*row)