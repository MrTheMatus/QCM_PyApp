# main.py
import sys
from PyQt5 import QtWidgets
from ui.ui_main2 import Ui_AffordableQCM  # Import the generated UI
from app.data_handler import DataHandler
from app.material_library import MaterialLibrary  # Material library logic

class MainApp(QMainWindow, Ui_AffordableQCM):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize the material library
        self.material_library = MaterialLibrary()

        # Connect signals
        self.addButton.clicked.connect(self.add_material)
        self.updateButton.clicked.connect(self.update_material)
        self.deleteButton.clicked.connect(self.delete_material)
        self.fetchButton.clicked.connect(self.load_materials)
        self.materialsListWidget.itemClicked.connect(self.populate_material_form)

        # Load materials on startup
        self.load_materials()

    def load_materials(self):
        """Load materials from the database and display in the list widget."""
        self.materialsListWidget.clear()
        materials = self.material_library.get_materials()
        for material in materials:
            item = QListWidgetItem(f"{material['name']} ({material['density']} {material['unit']})")
            item.setData(QtCore.Qt.UserRole, material['id'])  # Store material ID in the item
            self.materialsListWidget.addItem(item)

    def add_material(self):
        """Add a new material to the database."""
        name = self.materialEditLineEdit.text()
        density = self.densityEditLineEdit.text()
        unit = self.materialunitComboBox.currentText()

        if name and density and unit:
            self.material_library.add_material(name, float(density), unit)
            self.load_materials()

    def update_material(self):
        """Update the selected material in the database."""
        selected_item = self.materialsListWidget.currentItem()
        if not selected_item:
            return

        material_id = selected_item.data(QtCore.Qt.UserRole)
        name = self.materialEditLineEdit.text()
        density = self.densityEditLineEdit.text()
        unit = self.materialunitComboBox.currentText()

        if name and density and unit:
            self.material_library.update_material(material_id, name, float(density), unit)
            self.load_materials()

    def delete_material(self):
        """Delete the selected material from the database."""
        selected_item = self.materialsListWidget.currentItem()
        if not selected_item:
            return

        material_id = selected_item.data(QtCore.Qt.UserRole)
        self.material_library.delete_material(material_id)
        self.load_materials()

    def populate_material_form(self, item):
        """Populate the form fields with the selected material's data."""
        material_id = item.data(QtCore.Qt.UserRole)
        material = self.material_library.get_material_by_id(material_id)

        if material:
            self.materialEditLineEdit.setText(material['name'])
            self.densityEditLineEdit.setText(str(material['density']))
            self.materialunitComboBox.setCurrentText(material['unit'])

# Entry point
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainApp()
    mainWindow.show()
    sys.exit(app.exec_())
