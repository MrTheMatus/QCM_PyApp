# material_library.py
from app.data_handler import DataHandler

class MaterialLibrary:
    def __init__(self):
        self.db_handler = DataHandler()

    def get_materials(self):
        # Fetch materials from SQLite and return as list
        # Example: SELECT * FROM materials
        pass
