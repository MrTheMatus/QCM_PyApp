from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtCore import QTimer
from ui.ui_main import Ui_AffordableQCM
from app.worker import Worker
from utils.constants import Constants, SourceType
from utils.popUp import PopUp
from app.material_library import MaterialLibrary
from datetime import datetime
import logging
import sqlite3
import csv

logging.basicConfig(level=logging.INFO)

def log_calls(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Called function: {func.__name__} | args: {args} | kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

def log_all_methods(cls):
    for attr_name, attr_value in list(cls.__dict__.items()):
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, log_calls(attr_value))
    return cls

@log_all_methods
class ControlMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, port=None, bd=115200, samples=500):
        super().__init__()
        self.ui = Ui_AffordableQCM()
        self.ui.setupUi(self)
        self.setWindowTitle("Control Main Window")

        self.db_path = "deploy/db/database.db"
        self.process_id = None
        self.conn = self._initialize_db_connection()

        self.is_recording = False
        self.x_data = []
        self.y_data = []

        self.worker = Worker()

        self.ui.cBox_Source.addItems(Constants.app_sources)
        self.material_library = MaterialLibrary(db_path=self.db_path)
        self.ui.stackedWidget.setCurrentIndex(0)
        self._configure_plot()
        self._configure_timers()
        self._configure_signals()
        self._source_changed()
        self.ui.cBox_Source.setCurrentIndex(SourceType.serial.value)
        self.ui.sBox_Samples.setValue(samples)
        self._enable_ui(True)

    def switch_page(self, index):
        if 0 <= index < self.ui.stackedWidget.count():
            self.ui.stackedWidget.setCurrentIndex(index)
            if self.ui.stackedWidget.currentWidget().objectName() == "materialsPage":
                self.load_materials()

    def start(self, checked=False):
        """
        Starts data acquisition.
        """
        logging.info("Starting acquisition...")
        self.worker = Worker(
            port=self.ui.cBox_Port.currentText(),
            speed=float(self.ui.cBox_Speed.currentText()),
            samples=self.ui.sBox_Samples.value(),
            source=self._get_source(),
            export_enabled=self.ui.chBox_export.isChecked(),
        )
        self.worker.reset_buffers(self.ui.sBox_Samples.value())
        if self.worker.start():
            self._timer_plot.start(Constants.plot_update_ms)
            self._enable_ui(False)
        else:
            PopUp.warning(self, Constants.app_title, "Port not available.")


    def stop(self, *args, **kwargs):
        self.worker.stop()
        self._timer_plot.stop()
        self._enable_ui(True)
        if self.conn:
            self.conn.close()

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.start_recording()
            self.ui.recordButton.setText("Stop Recording")
        else:
            self.stop_recording()
            self.ui.recordButton.setText("Start Recording")

    def start_recording(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO Process (process_name, start_time) VALUES (?, ?)
                """,
                ("Recording", datetime.now()),
            )
            self.process_id = cursor.lastrowid
            self.conn.commit()
            logging.info(f"Recording started with process ID: {self.process_id}")
        except sqlite3.Error as e:
            logging.error(f"Failed to start recording: {e}")

    def stop_recording(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE Process SET end_time = ? WHERE process_id = ?
                """,
                (datetime.now(), self.process_id),
            )
            self.conn.commit()
            logging.info(f"Recording stopped for process ID: {self.process_id}")
        except sqlite3.Error as e:
            logging.error(f"Failed to stop recording: {e}")

    def _update_plot(self):
        self.worker.consume_queue()
        time_data = self.worker.get_time_buffer()

        if not time_data.size:
            logging.warning("Time data is empty, skipping plot update.")
            return

        self._plt.clear()
        self._plt_4.clear()
        self._plt_2.clear()
        self._plt_6.clear()

        for idx in range(self.worker.get_lines()):
            signal_data = self.worker.get_values_buffer(idx)

            if signal_data.size:
                # Main connection page plot
                self._plt.plot(x=time_data, y=signal_data, pen=Constants.plot_colors[idx])

                # Additional plots
                if idx == 0 and signal_data.size > 0:
                    self._plt_6.plot(x=time_data, y=signal_data, pen=Constants.plot_colors[idx])
                    self._plt_2.plot(x=time_data, y=signal_data - signal_data[0], pen=Constants.plot_colors[idx])
                    thickness = (signal_data - signal_data[0]) / Constants.density_factor  # Replace with correct calculation
                    self._plt_4.plot(x=time_data, y=thickness, pen=Constants.plot_colors[idx])

                    # Update the frequency line edit
                    current_frequency = signal_data[-1]
                    self.ui.frequencyLineEdit.setText(f"{current_frequency:.2f}")
            else:
                logging.warning(f"Signal data for line {idx} is empty.")

                if self.is_recording:
                    self._save_to_database(signal_data[-1], signal_data[-1] - tare, (signal_data[-1] - tare) / density)

    def _save_to_database(self, frequency, frequency_change, thickness):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO ProcessData (timestamp, frequency, frequency_change, thickness)
                VALUES (?, ?, ?, ?)
            """, (datetime.now(), frequency, frequency_change, thickness))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to insert data into database: {e}")

    def _enable_ui(self, enabled):
        self.ui.cBox_Port.setEnabled(enabled)
        self.ui.cBox_Speed.setEnabled(enabled)
        self.ui.pButton_Start.setEnabled(enabled)
        self.ui.chBox_export.setEnabled(enabled)
        self.ui.cBox_Source.setEnabled(enabled)
        self.ui.pButton_Stop.setEnabled(not enabled)

    def _configure_plot(self):
        self.ui.plt.setAntialiasing(True)
        self._plt = self.ui.plt.addPlot(row=0, col=0)
        self._plt.setLabel('bottom', Constants.plot_xlabel_title, Constants.plot_xlabel_unit)

        # Plot for thickness (plt_4)
        self.ui.plt_4_thickness.setAntialiasing(True)
        self._plt_4 = self.ui.plt_4_thickness.addPlot(row=0, col=0)
        self._plt_4.setLabel('bottom', "Time", "s")
        self._plt_4.setLabel('left', "Thickness", "nm")

        # Plot for frequency change (plt_2)
        self.ui.plt_2_changeFreq.setAntialiasing(True)
        self._plt_2 = self.ui.plt_2_changeFreq.addPlot(row=0, col=0)
        self._plt_2.setLabel('bottom', "Time", "s")
        self._plt_2.setLabel('left', "Frequency Change", "Hz")

        # Plot for frequency (plt_6)
        self.ui.plt6_Freq.setAntialiasing(True)
        self._plt_6 = self.ui.plt6_Freq.addPlot(row=0, col=0)
        self._plt_6.setLabel('bottom', "Time", "s")
        self._plt_6.setLabel('left', "Frequency", "Hz")


    def _configure_timers(self):
        self._timer_plot = QTimer(self)
        self._timer_plot.timeout.connect(self._update_plot)

    def _configure_signals(self):
        self.ui.fetchButton.clicked.connect(self.load_materials)
        self.ui.addButton.clicked.connect(self.add_material)
        self.ui.updateButton.clicked.connect(self.update_material)
        self.ui.deleteButton.clicked.connect(self.delete_material)
        self.ui.materialsListWidget.itemClicked.connect(self.populate_material_form)
        self.ui.pButton_Start.clicked.connect(self.start)
        self.ui.pButton_Stop.clicked.connect(self.stop)
        self.ui.sBox_Samples.valueChanged.connect(self._update_sample_size)
        self.ui.cBox_Source.currentIndexChanged.connect(self._source_changed)

        # Connect all navigation buttons to switch_page with corresponding page indices
        self.ui.homeButton.clicked.connect(lambda: self.switch_page(0))
        self.ui.databaseButton.clicked.connect(lambda: self.switch_page(2))
        self.ui.plotsButton.clicked.connect(lambda: self.switch_page(3))
        self.ui.connectionButton.clicked.connect(lambda: self.switch_page(4))
        self.ui.settingsButton.clicked.connect(lambda: self.switch_page(5))
        self.ui.helpButton.clicked.connect(lambda: self.switch_page(6))
        self.ui.infoButton.clicked.connect(lambda: self.switch_page(7))


    def _update_sample_size(self):
        if self.worker:
            self.worker.reset_buffers(self.ui.sBox_Samples.value())

    def _source_changed(self, index=None):
        """
        Updates the source and dependent combo boxes on change.
        """
        source = self._get_source()  # Fetch the source type based on current index
        logging.info(f"Scanning source {source.name}")
        
        # Clear and repopulate combo boxes
        self.ui.cBox_Port.clear()
        self.ui.cBox_Speed.clear()
        ports = Worker.get_source_ports(source)
        speeds = Worker.get_source_speeds(source)
        if ports:
            self.ui.cBox_Port.addItems(ports)
        if speeds:
            self.ui.cBox_Speed.addItems(speeds)
        if source == SourceType.serial and speeds:
            self.ui.cBox_Speed.setCurrentIndex(len(speeds) - 1)


    def _get_source(self):
        return SourceType(self.ui.cBox_Source.currentIndex())

    def load_materials(self, *args, **kwargs):
        """Load materials from the database and display them in the list widget."""
        self.ui.materialsListWidget.clear()
        materials = self.material_library.get_materials()
        if not materials:
            logging.warning("No materials found in the database.")
            return
        for material in materials:
            item = QListWidgetItem(f"{material['name']} ({material['density']} g/cm³)")
            item.setData(QtCore.Qt.UserRole, material['id'])
            self.ui.materialsListWidget.addItem(item)
        logging.info("Materials loaded successfully.")


    def add_material(self, *args, **kwargs):
        """Add a new material to the database."""
        name = self.ui.materialEditLineEdit.text()
        density = self.ui.densityEditLineEdit.text()

        if name and density:
            self.material_library.add_material(name, float(density))
            self.load_materials()
        logging.info("Material added successfully.")

    def update_material(self, *args, **kwargs):
        """Update the selected material in the database."""
        selected_item = self.ui.materialsListWidget.currentItem()
        if not selected_item:
            logging.warning("No material selected for update.")
            return

        material_id = selected_item.data(QtCore.Qt.UserRole)
        name = self.ui.materialEditLineEdit.text()
        density = self.ui.densityEditLineEdit.text()

        if name and density:
            self.material_library.update_material(material_id, name, float(density))
            self.load_materials()
        logging.info(f"Material with ID {material_id} updated successfully.")

    def delete_material(self, *args, **kwargs):
        """Delete the selected material from the database."""
        selected_item = self.ui.materialsListWidget.currentItem()
        if not selected_item:
            logging.warning("No material selected for deletion.")
            return

        material_id = selected_item.data(QtCore.Qt.UserRole)
        self.material_library.delete_material(material_id)
        self.load_materials()
        logging.info(f"Material with ID {material_id} deleted successfully.")

    def populate_material_form(self, item):
        material_id = item.data(QtCore.Qt.UserRole)
        material = self.material_library.get_material_by_id(material_id)
        if material:
            self.ui.materialEditLineEdit.setText(material['name'])
            self.ui.densityEditLineEdit.setText(str(material['density']))

    def _initialize_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Process (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_name TEXT,
                    start_time DATETIME,
                    end_time DATETIME
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ProcessData (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    frequency REAL,
                    frequency_change REAL,
                    thickness REAL,
                    FOREIGN KEY (process_id) REFERENCES Process (id)
                )
            """)
            conn.commit()
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return None