from .tables.file import FileTable

import sqlite3
import os




class UserDB():

    path = 'db/user.db'

    def __init__(self) -> None:
        root = os.environ.get('DATA_PATH', 'data/')
        self.db_path = os.path.join(root, self.path)
        self.files = FileTable()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)