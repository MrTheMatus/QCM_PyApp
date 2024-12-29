from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer
from ui.ui_main import Ui_AffordableQCM
from app.worker import Worker
from utils.constants import Constants, SourceType
from utils.popUp import PopUp
from app.material_library import MaterialLibrary
from datetime import datetime, timedelta
import logging
import sqlite3
import csv
from time import time, sleep
from utils.constants import Constants
from PyQt5 import QtCore, QtGui, QtWidgets
import webbrowser
from utils.architecture import Architecture

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

        # Initialize recording state
        self.is_recording = False
        self.process_id = None

        # Configure record button
        self.ui.recordButton.clicked.connect(self.toggle_recording)

        # Initialize material handling
        self.current_density = None
        self.current_materialName = None
        self._populate_material_combobox()

        self._last_db_insert = datetime.now()

    def switch_page(self, index):
        if 0 <= index < self.ui.stackedWidget.count():
            self.ui.stackedWidget.setCurrentIndex(index)
            if self.ui.stackedWidget.currentWidget().objectName() == "materialsPage":
                self.load_materials()

    def start(self, checked=False, *args, **kwargs):
        """
        Starts data acquisition.
        """
        logging.info("Starting acquisition...")
        self.current_density = self.ui.materialComboBox.currentData()
        self.current_materialName = self.ui.materialComboBox.currentText()
        self.worker = Worker(
            port=self.ui.cBox_Port.currentText(),
            speed=float(self.ui.cBox_Speed.currentText()),
            samples=self.ui.sBox_Samples.value(),
            source=self._get_source(),
            export_enabled=self.ui.chBox_export.isChecked(),
            material_density=self.current_density,
        )
        self.worker.reset_buffers(self.ui.sBox_Samples.value())
        if self.worker.start():
            self._timer_plot.start(Constants.plot_update_ms)
            self._enable_ui(False)
        else:
            PopUp.warning(self, Constants.app_title, "Port not available.")


    def stop(self, checked=False, *args, **kwargs):
        """Stop acquisition and cleanup
        Args:
            checked (bool): Signal parameter from QPushButton click
        """
        try:
            self._timer_plot.stop()
            self._enable_ui(True)
            self.worker.stop()
            
            if self.is_recording:
                self.stop_recording()
                self.ui.recordButton.setText("Start Recording")
                self.is_recording = False
                self.switch_record_button_icon(self.is_recording)
        except Exception as e:
            logging.error(f"Error during stop: {e}")

    def toggle_recording(self, checked=False, *args, **kwargs):
        """Toggle recording state
        Args:
            checked (bool): Signal parameter from QPushButton click
        """
        try:
            if not self.conn or self.conn.total_changes < 0:
                self.conn = self._initialize_db_connection()
                
            if not self.is_recording:
                self.start_recording()
                self.ui.recordButton.setText("Stop Recording")
            else:
                self.stop_recording() 
                self.ui.recordButton.setText("Start Recording")
                
            self.is_recording = not self.is_recording
            self.switch_record_button_icon(self.is_recording)
            
        except Exception as e:
            logging.error(f"Recording toggle failed: {e}")
            QMessageBox.warning(self, Constants.app_title, "Failed to toggle recording")
            self.is_recording = False
            self.ui.recordButton.setText("Start Recording")

    def start_recording(self, *args, **kwargs):
        """Start recording data to database"""
        try:
            if not self.conn:
                self.conn = self._initialize_db_connection()
        
            process_name = self.ui.processNameLineEdit.text().strip()
            if not process_name:
                process_name = 'Unnamed_process'
                
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO Process (process_name, start_time) VALUES (?, ?)",
                (process_name, datetime.now())
            )
            self.process_id = cursor.lastrowid
            self.conn.commit()
            logging.info(f"Recording started with ID: {self.process_id}")
            
        except sqlite3.Error as e:
            logging.error(f"Failed to start recording: {e}")
            raise

    def stop_recording(self, *args, **kwargs):
        """Stop recording data to database"""
        try:
            if not self.conn:
                logging.error("No database connection")
                return
                
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE Process SET end_time = ? WHERE process_id = ?",
                (datetime.now(), self.process_id)
            )
            self.conn.commit()
            logging.info(f"Recording stopped for process ID: {self.process_id}")
            
        except sqlite3.Error as e:
            logging.error(f"Failed to stop recording: {e}")
            raise

    def _update_plot(self, *args, **kwargs):
        """Updates all plots with current data"""
        self.worker.consume_queue()
        time_data, plot_data, n_plots = self.worker.prepare_plot_data()
        
        if time_data is None or not time_data.size or n_plots == 0:
            return
            
        # Clear all plots
        self._plt.clear()
        self._plt_4.clear() 
        self._plt_2.clear()
        self._plt_6.clear()

        # Debug plot data before processing
        logging.debug(f"Plot data: {plot_data}")
        
        # Get first channel data
        channel_data = plot_data[0] if isinstance(plot_data, list) else plot_data
        
        if channel_data['signal'] is not None and channel_data['signal'].size > 0:
            # Main plot 
            self._plt.plot(x=time_data, y=channel_data['signal'], 
                        pen=Constants.plot_colors[0])
            
            # Get latest values
            current_frequency = float(channel_data['signal'][0])
            current_thickness = float(channel_data['thickness'][0]) if channel_data['thickness'] is not None and channel_data['thickness'].size > 0 else 0.0
            logging.info(f"cur freq data: {current_frequency:.2f}")
            logging.info(f"cur th data: {current_thickness:.2f}")
            #sleep(2)
            # Update displays
            self.ui.frequencyLineEdit.setText(f"{current_frequency:.2f}")
            self.ui.thicknessLineEdit.setText(f"{current_thickness:.2f}")
            self.ui.lcdNumberFreq.display(f"{current_frequency:.2f}")
            self.ui.lcdNumberThickness.display(f"{current_thickness:.2f}")
            
            # Debug values
            logging.debug(f"Updated displays - Frequency: {current_frequency:.2f}, Thickness: {current_thickness:.2f}")
            
            # Plot updates for first channel
            self._plt_6.plot(x=time_data, y=channel_data['signal'],
                         pen=Constants.plot_colors[0])
            
            if channel_data['frequency_change'] is not None and channel_data['frequency_change'].size > 0:
                self._plt_2.plot(x=time_data, y=channel_data['frequency_change'],
                             pen=Constants.plot_colors[0])
            
            if channel_data['thickness'] is not None and channel_data['thickness'].size > 0:
                self._plt_4.plot(x=time_data, y=channel_data['thickness'],
                             pen=Constants.plot_colors[0])

            # Save to database if recording
            if self.is_recording:
                self._save_to_database(
                    current_frequency,
                    channel_data['frequency_change'][-1] if channel_data['frequency_change'] is not None and channel_data['frequency_change'].size > 0 else 0,
                    current_thickness
                )

    def _should_insert_to_db(self, *args, **kwargs):
        time_diff = datetime.now() - self._last_db_insert
        return time_diff >= timedelta(microseconds=Constants.MIN_STORAGE_INTERVAL_MS)

    def _save_to_database(self, frequency, frequency_change, thickness):
        logging.warning(
            "_save_to_database called: freq=%.2f, freq_change=%.2f, thickness=%.2f, "
            "is_recording=%s, process_id=%s",
            frequency, frequency_change, thickness,
            self.is_recording, self.process_id
        )

        if not self.is_recording or self.process_id is None:
            logging.warning("Exiting _save_to_database: is_recording=%s, process_id=%s", 
                        self.is_recording, self.process_id)
            return

        if not self._should_insert_to_db():
            logging.warning("Exiting _save_to_database: _should_insert_to_db returned False.")
            return

        try:
            current_time = datetime.now()
            # Log just before inserting
            logging.warning(
                "Inserting record to DB at %s: process_id=%s, frequency=%.2f, freq_change=%.2f, "
                "thickness=%.2f, material=%s",
                current_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                self.process_id,
                frequency,
                frequency_change,
                thickness,
                self.current_materialName
            )

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO ProcessData 
                (process_id, frequency, frequency_change, thickness, material_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self.process_id,
                    float(frequency),
                    float(frequency_change),
                    float(thickness),
                    self.current_materialName,
                    current_time
                )
            )
            self.conn.commit()
            self._last_db_insert = current_time

            logging.warning("DB insert successful. Updated _last_db_insert to %s", current_time)
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")


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
        self.ui.materialComboBox.currentIndexChanged.connect(self._material_changed)

        # Connect all navigation buttons to switch_page with corresponding page indices
        self.ui.homeButton.clicked.connect(lambda: self.switch_page(0))
        self.ui.connectionButton.clicked.connect(lambda: self.switch_page(1))
        self.ui.plotsButton.clicked.connect(lambda: self.switch_page(2))
        self.ui.databaseButton.clicked.connect(lambda: self.switch_page(3))
        self.ui.settingsButton.clicked.connect(lambda: self.switch_page(4))
        self.ui.infoButton.clicked.connect(lambda: self.switch_page(5))
        self.ui.helpButton.clicked.connect(self.open_help_documentation)

    def _update_sample_size(self, *args, **kwargs):
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
        self._populate_material_combobox()
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

    def closeEvent(self, event):
        """Handle application close"""
        try:
            if self.worker.is_running():
                self.stop()
            if self.conn:
                self.conn.close()
            event.accept()
        except Exception as e:
            logging.error(f"Error during close: {e}")
            event.accept()

    def _populate_material_combobox(self):
        """Populate material combo box with materials from database"""
        try:
            self.ui.materialComboBox.clear()
            materials = self.material_library.get_materials()
            for material in materials:
                self.ui.materialComboBox.addItem(
                    f"{material['name']} ({material['density']} g/cm³)", 
                    material['density']
                )
            # Set initial density
            if self.ui.materialComboBox.count() > 0:
                self.current_density = self.ui.materialComboBox.currentData()
                self.current_materialName = self.ui.materialComboBox.currentText()
            logging.debug("Material combo box populated")
        except Exception as e:
            logging.error(f"Error populating material combo box: {e}")

    def _material_changed(self, *args, **kwargs):
        """Handle material change."""
        if self.is_recording:
            QMessageBox.warning(self, Constants.app_title, "Cannot change material during recording")
            self.ui.materialComboBox.blockSignals(True)
            self.ui.materialComboBox.setCurrentIndex(self.ui.materialComboBox.findData(self.current_density))
            self.ui.materialComboBox.blockSignals(False)
            return
        selected_material = self.ui.materialComboBox.currentData()
        self.current_density = selected_material
        self.current_materialName = self.ui.materialComboBox.currentText()

    def switch_record_button_icon(self, is_recording):
        """Switch the icon of the record button based on the recording state."""
        icon = QtGui.QIcon()
        if is_recording:
            icon.addPixmap(QtGui.QPixmap(".\\ui\\../images/stop-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(".\\ui\\../images/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.recordButton.setIcon(icon)

    def open_help_documentation(self, *args, **kwargs):
        """Opens the project documentation."""
        doc_path = "docs/Project_Documentation.html"
        base_path = Architecture.get_path()
        full_path = f"{base_path}/{doc_path}"
        try:
            webbrowser.open(full_path)
            logging.info(f"Opened documentation: {full_path}")
        except Exception as e:
            logging.error(f"Failed to open documentation: {e}")
            QMessageBox.warning(self, "Error", f"Cannot open documentation: {e}")