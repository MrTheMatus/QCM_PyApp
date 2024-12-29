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
from app.setup_library import SetupLibrary
from PyQt5 import QtCore, QtGui, QtWidgets
import webbrowser
from utils.architecture import Architecture
from logging.handlers import TimedRotatingFileHandler
import os
from PyQt5.QtGui import QStandardItemModel, QStandardItem


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

class LogHandler(logging.Handler):
    def __init__(self, line_edit):
        super().__init__()
        self.line_edit = line_edit

    def emit(self, record):
        log_entry = self.format(record)
        self.line_edit.setText(log_entry)

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
        self.setup_library = SetupLibrary(db_path=self.db_path)

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

        # Configure logging
        self._configure_logging()

        self.edited_row_ids = set()  # Track edited rows by their IDs
        self.load_setup_constants()

    def _configure_logging(self):
        """Configure logging settings and handlers."""
        self.ui.logComboBox.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.ui.logComboBox.currentIndexChanged.connect(self._set_logging_level)
        self._set_logging_level()

        # Ensure the log directory exists
        log_dir = "./logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure TimedRotatingFileHandler
        current_date = datetime.now().strftime("%Y_%m_%d")  # Format the current date
        log_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, f"log_{current_date}.txt"), 
        when="midnight", 
        interval=1, 
        backupCount=7)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(log_handler)

    def _set_logging_level(self, *args, **kwargs):
        """Set the logging level based on the combo box selection."""
        level = self.ui.logComboBox.currentText()
        logging.getLogger().setLevel(getattr(logging, level))
        logging.info(f"Logging level set to {level}")

    def switch_page(self, index):
        if 0 <= index < self.ui.stackedWidget.count():
            self.ui.stackedWidget.setCurrentIndex(index)
            if self.ui.stackedWidget.currentWidget().objectName() == "materialsPage":
                self.load_materials()
            if self.ui.stackedWidget.currentWidget().objectName() == "settingsPage":
                self.load_setup_constants()

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

        self.ui.settingsfetchButton.clicked.connect(self.load_setup_constants)
        self.ui.setupComboBox.currentIndexChanged.connect(self.setup_selected)

        self.ui.settingsaddButton.clicked.connect(self.add_setup_row)
        self.ui.settingsdeleteButton.clicked.connect(self.delete_setup_row)
        self.ui.settingsupdateButton.clicked.connect(self.update_setup_row)
        self.ui.commitButton.clicked.connect(self.commit_changes)
        self.ui.rollbackButton.clicked.connect(self.rollback_changes)



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

    def load_setup_constants(self, *args, **kwargs):
        """Load setup constants into the QTableView."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM SetupConstants")
            rows = cursor.fetchall()
            
            # Create a model for QTableView
            model = QStandardItemModel(len(rows), 7)  # Rows, columns
            model.setHorizontalHeaderLabels([
                "ID", "Quartz Density", "Shear Modulus", "Area", "Tooling Factor", "Description", "Created At"
            ])
            
            # Populate the model
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QStandardItem(str(value))
                    item.setEditable(False)  # Make the item read-only
                    model.setItem(row_idx, col_idx, item)

            # Set the model to the QTableView
            self.ui.settingsTableView.setModel(model)

            # Populate the combo box with the setup descriptions
            self.populate_setup_combobox(rows)

            # Set column sizes for QTableView
            header = self.ui.settingsTableView.horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

            header.resizeSection(0, 45)   # ID - narrow
            header.resizeSection(1, 120)  # Quartz Density
            header.resizeSection(2, 120)  # Shear Modulus
            header.resizeSection(3, 65)   # Area
            header.resizeSection(4, 120)  # Tooling Factor
            header.resizeSection(5, 300)  # Description - wide
            header.resizeSection(6, 200)  # Created At

            logging.info("SetupConstants loaded into table view.")
        except sqlite3.Error as e:
            logging.error(f"Error loading setup constants: {e}")


    def setup_selected(self, *args, **kwargs):
        """Handle setup selection."""
        setup_id = self.ui.setupComboBox.currentData()
        if setup_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM SetupConstants WHERE id = ?", (setup_id,))
                setup = cursor.fetchone()
                if setup:
                    quartz_density, shear_modulus, area, tooling_factor = setup[1:5]
                    logging.info(f"Setup selected: {setup}")
                    # Use these values for thickness calculation
            except sqlite3.Error as e:
                logging.error(f"Error fetching selected setup: {e}")

    def populate_setup_combobox(self, setups, *args, **kwargs):
        """Populate the combo box with setup descriptions."""
        self.ui.setupComboBox.clear()
        for setup in setups:
            self.ui.setupComboBox.addItem(setup[5], setup[0])  # Description, ID
        logging.info("SetupComboBox populated.")

    def add_setup_row(self, *args, **kwargs):
        logging.info("Adding new setup row...")
        model = self.ui.settingsTableView.model()
        if not model:
            logging.error("No model found for settingsTableView.")
            return

        # Add a blank row with a placeholder ID
        new_row_index = model.rowCount()
        model.insertRow(new_row_index)

        placeholder_id = QStandardItem("NEW")
        placeholder_id.setEditable(False)  # ID should not be editable
        model.setItem(new_row_index, 0, placeholder_id)

        # Add editable blank items for other columns
        for col in range(1, model.columnCount()):
            item = QStandardItem("")
            item.setEditable(True)
            model.setItem(new_row_index, col, item)

        logging.info("New setup row added.")


    def delete_setup_row(self, *args, **kwargs):
        """Mark the selected row for deletion but defer database changes until commit."""
        model = self.ui.settingsTableView.model()
        if not model:
            logging.error("No model found for settingsTableView.")
            return

        # Get the selected rows
        selected_rows = self.ui.settingsTableView.selectionModel().selectedRows()
        if not selected_rows:
            logging.warning("No rows selected for deletion.")
            return

        for row in selected_rows:
            row_id_item = model.item(row.row(), 0)  # ID column
            if row_id_item:
                row_id = row_id_item.text()
                if row_id.isdigit():
                    # Add ID to a deferred deletion list
                    if not hasattr(self, "deferred_deletions"):
                        self.deferred_deletions = []
                    self.deferred_deletions.append(int(row_id))
                    logging.info(f"Row with ID {row_id} marked for deletion.")

            # Remove the row from the model
            model.removeRow(row.row())

        logging.info("Selected rows deleted from the view. Commit to apply changes.")


    def commit_changes(self, *args, **kwargs):
        """Commit changes from the table to the database."""
        logging.info("Committing changes...")
        model = self.ui.settingsTableView.model()
        if not model:
            logging.error("No model found for settingsTableView.")
            return

        # Handle deletions first
        if hasattr(self, "deferred_deletions") and self.deferred_deletions:
            for setup_id in self.deferred_deletions:
                self.setup_library.delete_setup(setup_id)
                logging.info(f"Deferred deletion committed for setup ID {setup_id}.")
            self.deferred_deletions.clear()

        # Process remaining rows for updates or inserts
        for row in range(model.rowCount()):
            id_item = model.item(row, 0)  # Column 0 is the ID
            quartz_density = model.item(row, 1).text()
            quartz_shear_modulus = model.item(row, 2).text()
            quartz_area = model.item(row, 3).text()
            tooling_factor = model.item(row, 4).text()
            description = model.item(row, 5).text()

            if id_item is None or id_item.text() == "NEW":
                # Handle new row (INSERT)
                new_id = self.setup_library.add_setup(
                    quartz_density,
                    quartz_shear_modulus,
                    quartz_area,
                    tooling_factor,
                    description
                )
                logging.info(f"New setup added with ID {new_id}")

                # Update the model with the new ID
                id_item.setText(str(new_id))
            elif int(id_item.text()) in self.edited_row_ids:
                # Handle existing row (UPDATE) only if its ID is in the edited_row_ids set
                self.setup_library.update_setup(
                    id_item.text(),
                    quartz_density,
                    quartz_shear_modulus,
                    quartz_area,
                    tooling_factor,
                    description
                )
                logging.info(f"Row with ID {id_item.text()} updated in database.")

        # Clear the edited rows set
        self.edited_row_ids.clear()

        # Reload the table after commit
        self.load_setup_constants()


    def rollback_changes(self, *args, **kwargs):
        """Reload setups from the database, discarding unsaved changes."""
        self.load_setup_constants()

        # Clear the deferred deletions list
        if hasattr(self, "deferred_deletions"):
            self.deferred_deletions.clear()

        logging.info("Changes rolled back. All deletions and edits discarded.")

    def update_setup_row(self, *args, **kwargs):
        """Enable editing for the selected row."""
        model = self.ui.settingsTableView.model()
        if not model:
            logging.error("No model found for settingsTableView.")
            return

        # Enable editing for the selected rows
        selected_rows = self.ui.settingsTableView.selectionModel().selectedRows()

        if not selected_rows:
            logging.warning("No rows selected for editing.")
            return

        for row in selected_rows:
            row_id_item = model.item(row.row(), 0)  # Column 0 is the ID
            if row_id_item and row_id_item.text().isdigit():
                row_id = int(row_id_item.text())
                self.edited_row_ids.add(row_id)  # Track the row ID for updates
                logging.info(f"Row with ID {row_id} enabled for editing.")

            # Enable editing for all columns in the selected row
            for col in range(model.columnCount()):
                item = model.item(row.row(), col)
                if item:
                    item.setEditable(True)

        logging.info("Selected rows are now editable.")


    def get_setup_constants(self, row_id, *args, **kwargs):
        """Get setup constants for the given row ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM SetupConstants WHERE id = ?", (row_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "quartz_density": row[1],
                "quartz_shear_modulus": row[2],
                "quartz_area": row[3],
                "tooling_factor": row[4],
                "description": row[5],
                "created_at": row[6],
            }
        return None

    def calculate_thickness(self, row_id, *args, **kwargs):
        """Calculate thickness using the setup constants for the given row ID."""
        setup_constants = self.get_setup_constants(row_id)
        if setup_constants:
            density = setup_constants["quartz_density"]
            modulus = setup_constants["quartz_shear_modulus"]
            area = setup_constants["quartz_area"]
            tooling_factor = setup_constants["tooling_factor"]
            return (density * modulus / area) * tooling_factor
        return None






