import sqlite3
from datetime import datetime
import os

from ..objects import Template




class FileTable:

    def __init__(self):
        path = os.environ.get('DATA_PATH', 'data/')
        self.db_path = os.path.join(path, 'db/naturaljob.db')
        
    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_template(self, conn:sqlite3.Connection, uuid:str, title:str, description:str, category:str, path:str) -> Template:

        date = datetime.now().strftime('%d/%m/%Y')
        conn.execute("""
            INSERT INTO USER_FILE (ID, Title, Description, Category, Date, Path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uuid, title, description, category, date, path))
        return Template(uuid, title, description, category, date, path)
    
    def get_templates(self):

        with self.connect() as conn:
            cursor = conn.execute("""
                SELECT ID, Title, Description, Category, Date, Path FROM USER_FILE
            """)
            rows = cursor.fetchall()
        return [Template(*row) for row in rows]
    
    def get_template(self, uuid:str) -> str:

        with self.connect() as conn:
            row = conn.execute("""
                SELECT ID, Title, Description, Category, Date, Path
                  FROM USER_FILE
                 WHERE ID = ?
            """, (uuid,)).fetchone()
        return Template(*row) if row else None
    
    def remove_template(self, conn:sqlite3.Connection, uuid:str) -> str:

        row = conn.execute("""
            SELECT ID, Title, Description, Category, Date, Path
            FROM USER_FILE
            WHERE ID = ?
        """, (uuid,)).fetchone()

        if row is None:
            return None  # nothing to remove

        conn.execute("DELETE FROM USER_FILE WHERE ID = ?", (uuid,))

        return Template(*row)