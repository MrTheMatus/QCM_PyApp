import sqlite3
import logging
from utils.logdecorator import log_all_methods

@log_all_methods
class ProcessLibrary:
    def __init__(self, db_path="deploy/db/database.db"):
        self.conn = sqlite3.connect(db_path)

    def get_processes(self):
        """Fetch all processes from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT process_id, process_name, start_time, end_time FROM Process")
            rows = cursor.fetchall()
            cursor.close()
            logging.info(f"Processes fetched: {rows}")
            return [
                {"id": row[0], "name": row[1], "start_time": row[2], "end_time": row[3]}
                for row in rows
            ]
        except Exception as e:
            logging.error(f"Error fetching processes: {e}")
            return []

    def add_process(self, name, start_time, end_time):
        """Add a new process to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO Process (process_name, start_time, end_time) VALUES (?, ?, ?)",
                (name, start_time, end_time)
            )
            self.conn.commit()
            cursor.close()
            logging.info(f"Process added: {name} ({start_time} - {end_time})")
        except Exception as e:
            logging.error(f"Error adding process: {e}")

    def update_process(self, process_id, name, start_time, end_time):
        """Update an existing process in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE Process SET process_name = ?, start_time = ?, end_time = ? WHERE process_id = ?",
                (name, start_time, end_time, process_id)
            )
            self.conn.commit()
            cursor.close()
            logging.info(f"Process updated: ID {process_id} to {name} ({start_time} - {end_time})")
        except Exception as e:
            logging.error(f"Error updating process ID {process_id}: {e}")

    def delete_process(self, process_id):
        """Delete a process from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Process WHERE process_id = ?", (process_id,))
            self.conn.commit()
            cursor.close()
            logging.info(f"Process deleted: ID {process_id}")
        except Exception as e:
            logging.error(f"Error deleting process ID {process_id}: {e}")

    def get_process_by_id(self, process_id):
        """Fetch a specific process by ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT process_id, process_name, start_time, end_time FROM Process WHERE process_id = ?",
                (process_id,)
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                return {"id": row[0], "name": row[1], "start_time": row[2], "end_time": row[3]}
            return None
        except Exception as e:
            logging.error(f"Error fetching process by ID {process_id}: {e}")
            return None