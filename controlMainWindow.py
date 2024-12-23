from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import QTimer
from pyqtgraph import AxisItem
from datetime import datetime
import logging
import sqlite3
import csv
from ui.ui_main import Ui_AffordableQCM
from app.worker import Worker
from utils.constants import Constants, SourceType
from utils.fileManager import FileManager
from app.material_library import MaterialLibrary
from utils.popUp import PopUp

class ControlMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, port=None, bd=115200, samples=500):
        super().__init__()
        self.ui = Ui_AffordableQCM()
        self.ui.setupUi(self)
        self.setWindowTitle("Control Main Window")

        # Attributes
        self.db_path = "deploy/db/database.db"
        self.process_id = None
        self.is_recording = False
        self.x_data, self.y_data = [], []
        self.worker = Worker()
        self.material_library = MaterialLibrary(db_path=self.db_path)

        # Configure UI and functionality
        self._configure_ui(samples)
        self._configure_plot()
        self._configure_timers()
        self._configure_signals()
        self._initialize_db_connection()

    def _configure_ui(self, samples):
        """Configure UI elements."""
        self.ui.cBox_Source.addItems(Constants.app_sources)
        self.ui.cBox_Source.setCurrentIndex(SourceType.serial.value)
        self.ui.sBox_Samples.setValue(samples)
        self.ui.recordButton.setIcon(QtGui.QIcon(".\\images\\play.png"))
        self._update_ports_and_speeds()

    def _configure_plot(self):
        """Set up plots with customized axes."""
        self._yaxis = self._create_axis("Frequency", "Hz")
        self._plt = self.ui.plt.addPlot(axisItems={'left': self._yaxis})
        self._plt.setLabel('bottom', Constants.plot_xlabel_title, Constants.plot_xlabel_unit)

    def _create_axis(self, label, unit):
        axis = AxisItem('left', maxTickLength=-5, showValues=True, text=label, units=unit)
        axis.setFixedWidth(77)
        return axis

    def _configure_timers(self):
        """Configure timers for batch saving and plot updates."""
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self._update_plot)

    def _configure_signals(self):
        """
        Configures the connections between signals and UI elements.
        """
        # Material management
        self.ui.fetchButton.clicked.connect(self.load_materials)  # Fetch and display materials
        self.ui.addButton.clicked.connect(self.add_material)      # Add a new material
        self.ui.updateButton.clicked.connect(self.update_material)  # Update an existing material
        self.ui.deleteButton.clicked.connect(self.delete_material)  # Delete the selected material
        self.ui.materialsListWidget.itemClicked.connect(self.populate_material_form)  # Populate form when item is clicked

        # General app actions
        self.ui.pButton_Start.clicked.connect(self.start)  # Start acquisition
        self.ui.pButton_Stop.clicked.connect(self.stop)    # Stop acquisition
        self.ui.sBox_Samples.valueChanged.connect(self._update_sample_size)  # Update sample size
        self.ui.cBox_Source.currentIndexChanged.connect(self._source_changed)  # Handle source change

        # Page navigation
        self.ui.homeButton.clicked.connect(lambda: self.switch_page(0))
        self.ui.recordButton.clicked.connect(self.toggle_recording)
        self.ui.databaseButton.clicked.connect(lambda: self.switch_page(2))
        self.ui.plotsButton.clicked.connect(lambda: self.switch_page(3))
        self.ui.connectionButton.clicked.connect(lambda: self.switch_page(4))
        self.ui.settingsButton.clicked.connect(lambda: self.switch_page(5))
        self.ui.helpButton.clicked.connect(lambda: self.switch_page(6))
        self.ui.infoButton.clicked.connect(lambda: self.switch_page(7))


    def start(self):
        """Start data acquisition."""
        self.worker = Worker(
            port=self.ui.cBox_Port.currentText(),
            speed=float(self.ui.cBox_Speed.currentText()),
            samples=self.ui.sBox_Samples.value(),
            source=self._get_source(),
            export_enabled=self.ui.chBox_export.isChecked()
        )
        if self.worker.start():
            self.plot_timer.start(Constants.plot_update_ms)
            self._toggle_ui(False)
        else:
            PopUp.warning(self, Constants.app_title, f"Port {self.ui.cBox_Port.currentText()} is not available")

    def stop(self):
        """Stop data acquisition."""
        self.plot_timer.stop()
        self.worker.stop()
        self._toggle_ui(True)

    def toggle_recording(self):
        """Toggle recording state and update the button icon."""
        self.is_recording = not self.is_recording
        icon_path = ".\\images\\stop-button.png" if self.is_recording else ".\\images\\play.png"
        self.ui.recordButton.setIcon(QtGui.QIcon(icon_path))
        if self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def _update_plot(self):
        """Update plot with data from Worker."""
        self.worker.consume_queue()
        self._plt.clear()
        for idx in range(self.worker.get_lines()):
            self._plt.plot(
                x=self.worker.get_time_buffer(),
                y=self.worker.get_values_buffer(idx),
                pen=Constants.plot_colors[idx]
            )

    def start_recording(self):
        """Initialize recording in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Process (process_name, start_time) VALUES (?, ?)""",
                ("Recording", datetime.now())
            )
            self.process_id = cursor.lastrowid

    def stop_recording(self):
        """
        Stop recording data and save any remaining buffered data.
        """
        if not self.is_recording:
            return

        # Finalize recording process
        self.worker.flush_to_db()  # Ensure all data in the buffer is saved to the DB
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Process SET end_time = ? WHERE process_id = ?",
                (datetime.now(), self.process_id)
            )
            conn.commit()
            logging.info(f"Stopped recording for process ID: {self.process_id}")
        except sqlite3.Error as e:
            logging.error(f"Failed to stop recording: {e}")
        finally:
            conn.close()

        # Reset recording state
        self.is_recording = False
        self.ui.recordButton.setIcon(QtGui.QIcon(".\\images\\play.png"))
        self.process_id = None
        logging.info("Recording stopped.")


    def _initialize_db_connection(self):
        """Test database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logging.info("Database connection initialized.")
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def _update_sample_size(self):
        """Update sample size in the Worker."""
        self.worker.reset_buffers(self.ui.sBox_Samples.value())

    def _update_ports_and_speeds(self):
        """Update available ports and speeds based on source."""
        source = self._get_source()
        self.ui.cBox_Port.clear()
        self.ui.cBox_Port.addItems(self.worker.get_source_ports(source) or [])
        self.ui.cBox_Speed.clear()
        self.ui.cBox_Speed.addItems(self.worker.get_source_speeds(source) or [])

    def _get_source(self):
        return SourceType(self.ui.cBox_Source.currentIndex())

    def load_materials(self):
        """
        Load materials from the database and display them in the materials list widget.
        """
        self.ui.materialsListWidget.clear()
        materials = self.material_library.get_materials()
        if not materials:
            logging.warning("No materials found in the database.")
            return

        for material in materials:
            item = QListWidgetItem(f"{material['name']} ({material['density']} g/cm³)")
            item.setData(QtCore.Qt.UserRole, material['id'])
            self.ui.materialsListWidget.addItem(item)

    def add_material(self):
        """Add a new material to the database."""
        name = self.ui.materialEditLineEdit.text()
        density = self.ui.densityEditLineEdit.text()
        if name and density:
            self.material_library.add_material(name, float(density))
            self.load_materials()

    def update_material(self):
        """Update the selected material."""
        selected_item = self.ui.materialsListWidget.currentItem()
        if selected_item:
            material_id = selected_item.data(QtCore.Qt.UserRole)
            name = self.ui.materialEditLineEdit.text()
            density = self.ui.densityEditLineEdit.text()
            if name and density:
                self.material_library.update_material(material_id, name, float(density))
                self.load_materials()

    def delete_material(self):
        """Delete the selected material."""
        selected_item = self.ui.materialsListWidget.currentItem()
        if selected_item:
            material_id = selected_item.data(QtCore.Qt.UserRole)
            self.material_library.delete_material(material_id)
            self.load_materials()

    def populate_material_form(self, item):
        """
        Populate the form fields with the selected material's data.
        """
        material_id = item.data(QtCore.Qt.UserRole)
        material = self.material_library.get_material_by_id(material_id)

        if material:
            self.ui.materialEditLineEdit.setText(material['name'])
            self.ui.densityEditLineEdit.setText(str(material['density']))
            logging.info(f"Material form populated with ID {material_id}: {material}")
        else:
            logging.warning(f"Material with ID {material_id} not found.")


    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker.is_running():
            self.stop()
        super().closeEvent(event)

    def switch_page(self, index):
        """
        Switch to the specified page in the QStackedWidget.
        Fetch materials if navigating to the materials page.
        """
        if 0 <= index < self.ui.stackedWidget.count():
            self.ui.stackedWidget.setCurrentIndex(index)
            logging.info(f"Switched to page {index}: {self.ui.stackedWidget.currentWidget().objectName()}")
            
            # Fetch materials if navigating to the materials page
            if self.ui.stackedWidget.currentWidget().objectName() == "materialsPage":
                self.load_materials()
        else:
            logging.warning(f"Invalid page index: {index}")

    def _source_changed(self):
        """
        Updates the source and dependent combo boxes when the source changes.
        """
        logging.info(f"Scanning source: {self._get_source().name}")
        # Clear boxes before adding new options
        self.ui.cBox_Port.clear()
        self.ui.cBox_Speed.clear()

        # Get the current source type
        source = self._get_source()
        ports = self.worker.get_source_ports(source)
        speeds = self.worker.get_source_speeds(source)

        # Populate the combo boxes with the available options
        if ports:
            self.ui.cBox_Port.addItems(ports)
        if speeds:
            self.ui.cBox_Speed.addItems(speeds)

        # Default to the highest speed for serial source
        if self._get_source() == SourceType.serial and speeds:
            self.ui.cBox_Speed.setCurrentIndex(len(speeds) - 1)

    def _get_source(self):
        """
        Gets the current source type based on the combo box index.
        :return: Current source type.
        :rtype: SourceType
        """
        return SourceType(self.ui.cBox_Source.currentIndex())
    
    def _toggle_ui(self, state):
        """
        Toggle the UI elements based on the given state.
        :param state: State to set the UI elements to.
        :type state: bool.
        """
        self.ui.pButton_Start.setEnabled(state)
        self.ui.pButton_Stop.setEnabled(not state)
        self.ui.cBox_Source.setEnabled(state)
        self.ui.cBox_Port.setEnabled(state)
        self.ui.cBox_Speed.setEnabled(state)
        self.ui.sBox_Samples.setEnabled(state)
        self.ui.chBox_export.setEnabled(state)
        self.ui.recordButton.setEnabled(not state)

    def _update_plot(self):
        """Update the plot with data from the Worker."""
        self.worker.consume_queue()
        self._plt.clear()
        for idx in range(self.worker.get_lines()):
            self._plt.plot(
                x=self.worker.get_time_buffer(),
                y=self.worker.get_values_buffer(idx),
                pen=Constants.plot_colors[idx]
            )   
    

    




    