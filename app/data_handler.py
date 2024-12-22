# data_handler.py
import sqlite3

class DataHandler:
    def __init__(self, db_name="app_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, timestamp TEXT, message TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY, name TEXT, coefficient REAL)''')
        self.conn.commit()

    def insert_log(self, timestamp, message):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO logs (timestamp, message) VALUES (?, ?)", (timestamp, message))
        self.conn.commit()
