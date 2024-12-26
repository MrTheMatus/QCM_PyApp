# data_handler.py
import sqlite3
from utils.logdecorator import log_calls, log_all_methods


@log_all_methods
class DataHandler:
    def __init__(self, db_name="app_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                density REAL NOT NULL,
                unit TEXT NOT NULL
            )
        ''')
        self.conn.commit()


    def insert_log(self, timestamp, message):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO logs (timestamp, message) VALUES (?, ?)", (timestamp, message))
        self.conn.commit()
