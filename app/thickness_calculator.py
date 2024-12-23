import sqlite3

class ThicknessCalculator:
    def __init__(self, db_path):
        self.db_path = db_path

    def calculate_thickness(self, frequency_change, material_id):
        """
        Calculate thickness using the Sauerbrey equation.
        """
        material_density = self._get_material_density(material_id)
        if material_density is None:
            raise ValueError(f"Material ID {material_id} not found in the database.")
        
        # Sauerbrey equation (simplified example):
        thickness = (frequency_change / material_density)  # Replace with full equation if necessary
        return thickness

    def _get_material_density(self, material_id):
        """
        Fetch material density from the database.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT density FROM Materials WHERE id = ?", (material_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
