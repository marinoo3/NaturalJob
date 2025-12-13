from .tables.offer import OfferTable

import sqlite3
import os




class OfferDB():

    path = 'db/offer.db'

    def __init__(self) -> None:
        root = os.environ.get('DATA_PATH', 'data/')
        self.db_path = os.path.join(root, self.path)
        self.files = OfferTable()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)