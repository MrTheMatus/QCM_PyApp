# material_library.py
from app.data_handler import DataHandler
from app.database_process import DatabaseProcess
import sqlite3

class MaterialLibrary:
    def __init__(self, db_path="deploy/db/database.db"):
        self.conn = sqlite3.connect(db_path)

    def get_materials(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT material_id, material_name, density, unit FROM Material")
        rows = cursor.fetchall()
        return [
            {"id": row[0], "name": row[1], "density": row[2], "unit": row[3]}
            for row in rows
        ]

    def add_material(self, name, density, unit):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Material (material_name, density, unit) VALUES (?, ?, ?)", (name, density, unit))
        self.conn.commit()

    def update_material(self, material_id, name, density, unit):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE Material SET material_name = ?, density = ?, unit = ? WHERE material_id = ?",
            (name, density, unit, material_id),
        )
        self.conn.commit()

    def delete_material(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Material WHERE material_id = ?", (material_id,))
        self.conn.commit()

    def get_material_by_id(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT material_id, material_name, density, unit FROM Material WHERE material_id = ?", (material_id,))
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "density": row[2], "unit": row[3]}
        return None
