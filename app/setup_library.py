# setup_library.py
import sqlite3
import logging
from utils.logdecorator import log_calls, log_all_methods

@log_all_methods
class SetupLibrary:
    def __init__(self, db_path="deploy/db/database.db"):
        self.conn = sqlite3.connect(db_path)

    def get_setups(self):
        """Fetch all setups from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description, created_at 
                FROM SetupConstants
            """)
            rows = cursor.fetchall()
            cursor.close()
            logging.info(f"Setups fetched: {rows}")
            return [
                {"id": row[0], "density": row[1], "modulus": row[2], "area": row[3], 
                 "tooling_factor": row[4], "description": row[5], "created_at": row[6]}
                for row in rows
            ]
        except sqlite3.Error as e:
            logging.error(f"Error fetching setups: {e}")
            return []

    def add_setup(self, quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description):
        """Add a new setup to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO SetupConstants (quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description) 
                VALUES (?, ?, ?, ?, ?)
            """, (quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description))
            self.conn.commit()
            cursor.close()
            logging.info(f"Setup added: {description}")
        except sqlite3.Error as e:
            logging.error(f"Error adding setup: {e}")

    def update_setup(self, setup_id, quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description):
        """Update an existing setup in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE SetupConstants 
                SET quartz_density = ?, quartz_shear_modulus = ?, quartz_area = ?, tooling_factor = ?, description = ? 
                WHERE id = ?
            """, (quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description, setup_id))
            self.conn.commit()
            cursor.close()
            logging.info(f"Setup updated: ID {setup_id}")
        except sqlite3.Error as e:
            logging.error(f"Error updating setup ID {setup_id}: {e}")

    def delete_setup(self, setup_id):
        """Delete a setup from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM SetupConstants WHERE id = ?", (setup_id,))
            self.conn.commit()
            cursor.close()
            logging.info(f"Setup deleted: ID {setup_id}")
        except sqlite3.Error as e:
            logging.error(f"Error deleting setup ID {setup_id}: {e}")
