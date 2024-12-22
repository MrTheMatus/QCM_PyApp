# main_app.py
import sys
from PyQt5 import QtWidgets
from ui.ui_main import Ui_MainWindow  # Import the generated UI
from app.data_handler import DataHandler
from app.material_library import MaterialLibrary  # Material library logic

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize database handler
        self.db_handler = DataHandler()
        
        # Initialize materials library
        self.material_library = MaterialLibrary()
        
        # Connect UI signals to slots
        self.loadButton.clicked.connect(self.load_materials)
        self.saveButton.clicked.connect(self.save_log)

    def load_materials(self):
        # Load materials data into UI (example)
        materials = self.material_library.get_materials()
        # populate materials in the UI as needed

    def save_log(self):
        # Log something to the database
        self.db_handler.insert_log("2024-10-22", "Sample log entry")

    def update_thickness(self, thickness_value):
        # Update thickness value on main screen from simulator data
        self.thicknessLabel.setText(f"Thickness: {thickness_value}")

# Entry point
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainApp()
    mainWindow.show()
    sys.exit(app.exec_())
