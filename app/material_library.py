# material_library.py
from app.data_handler import DataHandler
from app.database_process import DatabaseProcess
import sqlite3
import logging
from utils.logdecorator import log_calls, log_all_methods


@log_all_methods
class MaterialLibrary:
    def __init__(self, db_path="deploy/db/database.db"):
        self.conn = sqlite3.connect(db_path)

    

    def get_materials(self):
        """Fetch all materials from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT material_id, material_name, density FROM Material")
            rows = cursor.fetchall()
            cursor.close()
            logging.info(f"Materials fetched: {rows}")
            return [
                {"id": row[0], "name": row[1], "density": row[2]}
                for row in rows
            ]
        except Exception as e:
            logging.error(f"Error fetching materials: {e}")
            return []




    def add_material(self, name, density):
        """Add a new material to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO Material (material_name, density) VALUES (?, ?)",
                (name, density)
            )
            self.conn.commit()
            cursor.close()
            logging.info(f"Material added: {name} ({density} g/cm³)")
        except Exception as e:
            logging.error(f"Error adding material: {e}")



    def update_material(self, material_id, name, density):
        """Update an existing material in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE Material SET material_name = ?, density = ? WHERE material_id = ?",
                (name, density, material_id)
            )
            self.conn.commit()
            cursor.close()
            logging.info(f"Material updated: ID {material_id} to {name} ({density} g/cm³)")
        except Exception as e:
            logging.error(f"Error updating material ID {material_id}: {e}")

            
    def delete_material(self, material_id):
        """Delete a material from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Material WHERE material_id = ?", (material_id,))
            self.conn.commit()
            cursor.close()
            logging.info(f"Material deleted: ID {material_id}")
        except Exception as e:
            logging.error(f"Error deleting material ID {material_id}: {e}")


    def get_material_by_id(self, material_id):
        """Fetch a specific material by ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT material_id, material_name, density FROM Material WHERE material_id = ?",
                (material_id,)
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                return {"id": row[0], "name": row[1], "density": row[2]}
            return None
        except Exception as e:
            logging.error(f"Error fetching material by ID {material_id}: {e}")
            return None

    
