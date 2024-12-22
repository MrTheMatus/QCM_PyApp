import sqlite3
import multiprocessing
from time import sleep
from datetime import datetime
from utils.constants import Constants  # Adjust path as needed
from utils.logger import Logger  # Adjust path as needed

TAG = "DB"
BATCH_SIZE = 60  # Number of records to batch before committing

class DatabaseProcess(multiprocessing.Process):
    """
    Process to store and export data to an SQLite database.
    """
    def __init__(self, db_path, timeout=0.5):
        super().__init__()
        self._exit = multiprocessing.Event()
        self._store_queue = multiprocessing.Queue()
        self._db_path = db_path
        self._timeout = timeout
        self._conn = None

        Logger.i(TAG, "Database Process ready")

    def run(self):
        """
        Process monitors the queue and writes data to the SQLite database.
        """
        Logger.i(TAG, "Database Process starting...")
        self._initialize_database()
        
        while not self._exit.is_set():
            self._consume_queue()
            sleep(self._timeout)
        
        # Final check to empty the queue
        self._consume_queue()
        Logger.i(TAG, "Database Process finished")

    def _initialize_database(self):
        """
        Initialize the SQLite database with the required tables.
        """
        self._conn = sqlite3.connect(self._db_path)
        cursor = self._conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ProcessData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            frequency REAL,
            frequency_change REAL,
            thickness REAL
        )''')
        
        self._conn.commit()

    def add_data(self, frequency, frequency_change, thickness):
        """
        Add a new row of data to the queue.
        """
        self._store_queue.put((datetime.now(), frequency, frequency_change, thickness))

    def _consume_queue(self):
        """
        Writes data from the queue to the database in batches.
        """
        batch_data = []
        cursor = self._conn.cursor()

        # Gather data up to the batch size or until the queue is empty
        while not self._store_queue.empty() and len(batch_data) < BATCH_SIZE:
            data = self._store_queue.get(timeout=self._timeout / 10)
            batch_data.append(data)

        if batch_data:
            # Execute the batch insert
            cursor.executemany('''
                INSERT INTO ProcessData (timestamp, frequency, frequency_change, thickness)
                VALUES (?, ?, ?, ?)
            ''', batch_data)
            self._conn.commit()  # Commit the transaction after batch insert

    def stop(self):
        """
        Signal the process to stop.
        """
        Logger.i(TAG, "Database Process finishing...")
        self._exit.set()
        if self._conn:
            self._conn.close()
