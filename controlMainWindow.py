from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtCore import QTimer
from ui.ui_main import Ui_AffordableQCM  # Adjust if needed
from app.worker import Worker  # Ensure Worker is imported correctly
from utils.constants import Constants, SourceType  # Adjust the path for your project structure
import logging
from utils.popUp import PopUp  # Adjust the path for Logger and PopUp classes
from utils.CSVProcess import CSVProcess
import csv
from enum import Enum
from utils.arguments import Arguments
from pyqtgraph import AxisItem
from app.material_library import MaterialLibrary
from datetime import datetime
from utils.fileManager import FileManager
import sqlite3

tare = 6000000
density = 10
#todo expand

class ControlMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, port=None, bd=115200, samples=500):
        super().__init__()
        self.ui = Ui_AffordableQCM()
        self.ui.setupUi(self)
        self.setWindowTitle("Control Main Window")
        

        self.db_path = "deploy/db/database.db"
        self.process_id = None  # Assign this when a process starts
        self.conn = self._initialize_db_connection()

        # Flag to track recording state
        self.is_recording = False
        self.process_id = None
        self.x_data = []
        self.y_data = []


        self._plt = None
        self.plt_4_thickness = None

        self.plt6_Freq = None
        self._timer_plot = None
        self.plt_2_changeFreq = None
        
        self.worker = Worker()

        # configures
        self.ui.cBox_Source.addItems(Constants.app_sources)
        # Initialize MaterialLibrary with the database path
        self.material_library = MaterialLibrary(db_path="deploy/db/database.db")
        # Initialize the materials_fetched flag
        #self.materials_fetched = False
        self.ui.stackedWidget.setCurrentIndex(0)
        self._configure_plot()
        self._configure_timers()
        self._configure_signals()

        #self.installEventFilter(self)

        # populate combo box for serial ports
        self._source_changed()
        self.ui.cBox_Source.setCurrentIndex(SourceType.serial.value)

        self.ui.sBox_Samples.setValue(samples)

        # enable ui
        self._enable_ui(True)
        pathname = self.ui.pathLineEdit.text()
        if pathname== '':
            pathname="default.csv"
        with open(pathname, 'w', newline='') as csvfile:
            fieldnames = ['Absolute Frequency', 'Frequency change', 'Thickness[nm]', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            csvfile.close()
    
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

    def start(self):
        """
        Starts the acquisition of the selected serial port.
        This function is connected to the clicked signal of the Start button.
        :return:
        """
        logging.info("TAG Clicked start")
        self.worker = Worker(port=self.ui.cBox_Port.currentText(),
                             speed=float(self.ui.cBox_Speed.currentText()),
                             samples=self.ui.sBox_Samples.value(),
                             source=self._get_source(),
                             export_enabled=self.ui.chBox_export.isChecked())
        if self.worker.start():
            self._timer_plot.start(Constants.plot_update_ms)
            self._enable_ui(False)
        else:
            logging.info("TAG Port is not available")
            PopUp.warning(self, Constants.app_title, "Selected port \"{}\" is not available"
                          .format(self.ui.cBox_Port.currentText()))

    def stop(self):
        """
        Stops the acquisition of the selected serial port.
        This function is connected to the clicked signal of the Stop button.
        :return:
        """
        logging.info("TAG Clicked stop")
        self._timer_plot.stop()
        self._enable_ui(True)
        self.worker.stop()

    def closeEvent(self, evnt):
        """
        Overrides the QTCloseEvent.
        This function is connected to the clicked signal of the close button of the window.
        :param evnt: QT evnt.
        :return:
        """
        if self.worker.is_running():
            logging.info("TAG Window closed without stopping capture, stopping it")
            self.stop()

    def _enable_ui(self, enabled):
        """
        Enables or disables the UI elements of the window.
        :param enabled: The value to be set at the enabled characteristic of the UI elements.
        :type enabled: bool
        :return:
        """
        self.ui.cBox_Port.setEnabled(enabled)
        self.ui.cBox_Speed.setEnabled(enabled)
        self.ui.pButton_Start.setEnabled(enabled)
        self.ui.chBox_export.setEnabled(enabled)
        self.ui.cBox_Source.setEnabled(enabled)
        self.ui.pButton_Stop.setEnabled(not enabled)

    def _configure_plot(self):
        """
        Configures specific elements of the PyQtGraph plots.
        :return:
        """
        self._yaxis = AxisItem('left', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True, text='Frequency', units='Hz')
        self._yaxis.setFixedWidth(77)
        self._yaxis.setWidth(77)

        self._yaxis2 = AxisItem('left', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True, text='thickness', units='nm')
        self._yaxis2.setFixedWidth(77)
        self._yaxis2.setWidth(77)

        self._yaxis3 = AxisItem('left', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True, text='Frequency', units='Hz')
        self._yaxis3.setFixedWidth(77)
        self._yaxis3.setWidth(77)

        self._yaxis4 = AxisItem('left', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True, text='Frequency', units='Hz')
        self._yaxis4.setFixedWidth(77)
        self._yaxis4.setWidth(77)

        self._yaxis.setLabel(show=True)
        self._yaxis.setGrid(grid=True)
        #self.ui.plt.setBackground(background=None)
        self.ui.plt.setAntialiasing(True)
        self._plt = self.ui.plt.addPlot(row=0, col=0, axisItems={'left':self._yaxis})
        self._plt.setLabel('bottom', Constants.plot_xlabel_title, Constants.plot_xlabel_unit)

        self.ui.plt_4_thickness.setAntialiasing(True)
        self._plt_4_thickness = self.ui.plt_4_thickness.addPlot(row=0, col=0, axisItems={'left':self._yaxis2})
        self._plt_4_thickness.setLabel('bottom', Constants.plot_xlabel_title, Constants.plot_xlabel_unit)


        self.ui.plt6_Freq.setAntialiasing(True)
        self._plt6_Freq = self.ui.plt6_Freq.addPlot(row=0, col=0, axisItems={'left':self._yaxis3})
        self._plt6_Freq.setLabel('bottom', Constants.plot_xlabel_title, Constants.plot_xlabel_unit)

        self.ui.plt_2_changeFreq.setAntialiasing(True)
        self._plt_2_changeFreq = self.ui.plt_2_changeFreq.addPlot(row=0, col=0, axisItems={'left':self._yaxis4})
        self._plt_2_changeFreq.setLabel('bottom', Constants.plot_xlabel_title, Constants.plot_xlabel_unit)


    def _configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self._timer_plot = QtCore.QTimer(self)
        self._timer_plot.timeout.connect(self._update_plot)

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

        

    def toggle_recording(self):
        if self.is_recording:
            # Stop recording
            self.stop_recording()
            self.ui.recordButton.setText("Start Recording")
            self.is_recording = False
        else:
            # Start recording
            self.start_recording()
            self.ui.recordButton.setText("Stop Recording")
            self.is_recording = True




    def _update_sample_size(self):
        """
        Updates the sample size of the plot.
        This function is connected to the valueChanged signal of the sample Spin Box.
        :return:
        """
        if self.worker is not None:
            logging.info("TAG Changing sample size")
            self.worker.reset_buffers(self.ui.sBox_Samples.value())

    def _update_plot(self):
        """
        Updates and redraws the graphics in the plot.
        This function us connected to the timeout signal of a QTimer.
        :return:
        """
        self.worker.consume_queue()
        pathname = self.ui.pathLineEdit.text()
        if pathname== '':
            pathname="default.csv"
            
        if not (FileManager.file_exists(pathname)):
            with open(pathname, 'w', newline='') as csvfile:
                fieldnames = ['Absolute Frequency', 'Frequency change', 'Thickness[nm]', 'Timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                pass
                writer.writeheader()
                csvfile.close()
        else:
            with open(pathname, 'a', newline='') as f_object:
               
                writer_object = csv.writer(f_object)
                # Pass the list as an argument into
                # the writerow()
                x_data=[]
                y_data=[]
                for idx in range(self.worker.get_lines()):
                    x_data=self.worker.get_time_buffer()
                    y_data=self.worker.get_values_buffer(idx)
                if len(x_data) > 0 and x_data[0] is not None:
                    self.ui.frequencyLineEdit.setText(str(y_data[0]) + " Hz")
                    List=[y_data[0],y_data[0]-tare,(y_data[0]-tare)/density,datetime.now()]
                    writer_object.writerow(List)
                    self.x_data.append(datetime.now())
                    self.y_data.append(y_data[0])
                   # Proceed with processing
                else:
                    logging.warning("x_data is empty or does not have a valid first element")
                    
        #Close the file object
                f_object.close()

        # plot data
        self._plt.clear()
        for idx in range(self.worker.get_lines()):
            self._plt.plot(x=self.worker.get_time_buffer(),
                           y=self.worker.get_values_buffer(idx),
                           pen=Constants.plot_colors[idx])
        self._plt_2_changeFreq.clear()
        for idx in range(self.worker.get_lines()):
            self._plt_2_changeFreq.plot(x=self.worker.get_time_buffer(),
                           y=self.worker.get_values_buffer(idx)-tare,
                           pen=Constants.plot_colors[idx])
        self._plt6_Freq.clear()
        for idx in range(self.worker.get_lines()):
            self._plt6_Freq.plot(x=self.worker.get_time_buffer(),
                           y=self.worker.get_values_buffer(idx),
                           pen=Constants.plot_colors[idx])
        
        self.ui.plt_4_thickness.clear()
        for idx in range(self.worker.get_lines()):
            self._plt_4_thickness.plot(x=self.worker.get_time_buffer(),
                           y=(self.worker.get_values_buffer(idx)-tare)/density,
                           pen=Constants.plot_colors[idx])



    def _source_changed(self):
        """
        Updates the source and depending boxes on change.
        This function is connected to the indexValueChanged signal of the Source ComboBox.
        :return:
        """
        logging.info("[G] Scanning source {}".format(self._get_source().name))
        # clear boxes before adding new
        self.ui.cBox_Port.clear()
        self.ui.cBox_Speed.clear()

        source = self._get_source()
        ports = self.worker.get_source_ports(source)
        speeds = self.worker.get_source_speeds(source)

        if ports is not None:
            self.ui.cBox_Port.addItems(ports)
        if speeds is not None:
            self.ui.cBox_Speed.addItems(speeds)
        if self._get_source() == SourceType.serial:
            self.ui.cBox_Speed.setCurrentIndex(len(speeds) - 1)

    def _get_source(self):
        """
        Gets the current source type.
        :return: Current Source type.
        :rtype: SourceType.
        """
        return SourceType(self.ui.cBox_Source.currentIndex())
    
    def load_materials(self):
        """Load materials from the database and display in the list widget."""
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


    def delete_material(self):
        """Delete the selected material from the database."""
        selected_item = self.ui.materialsListWidget.currentItem()
        if not selected_item:
            return

        material_id = selected_item.data(QtCore.Qt.UserRole)
        self.material_library.delete_material(material_id)
        self.load_materials()

    def populate_material_form(self, item):
        """
        Populate the form fields with the selected material's data.
        
        :param item: The QListWidgetItem that was clicked.
        """
        # Get the material ID stored in the item's data
        material_id = item.data(QtCore.Qt.UserRole)
        
        # Fetch the material details from the database
        material = self.material_library.get_material_by_id(material_id)

        # Populate the form fields with the material details
        if material:
            self.ui.materialEditLineEdit.setText(material['name'])
            self.ui.densityEditLineEdit.setText(str(material['density']))
            logging.info(f"Material form populated with ID {material_id}: {material}")
        else:
            logging.warning(f"Material with ID {material_id} not found")

    def _initialize_db_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Database connection initialized.")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def _save_plot_data(self, x_data, y_data):
        """
        Saves plot data into the ProcessData table for the current process.
        :param x_data: List of frequency changes (or x-axis data).
        :param y_data: List of absolute frequencies (or y-axis data).
        """
        if self.process_id is None:
            logging.warning("No active process. Data will not be saved.")
            return

        if not x_data or not y_data:
            logging.warning("No data to save in ProcessData.")
            return

        try:
            with self.conn:
                cursor = self.conn.cursor()
                # Calculate rate of change
                rate_of_change = self._calculate_rate_of_change(x_data)

                for x, y in zip(x_data, y_data):
                    cursor.execute("""
                        INSERT INTO ProcessData (
                            process_id, frequency, frequency_change, frequency_rate_of_change, unit
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (self.process_id, y, x, rate_of_change, "Hz"))
            
            logging.info(f"Process data successfully saved for process_id {self.process_id}.")
        except Exception as e:
            logging.error(f"Error saving process data: {e}")


    def _calculate_rate_of_change(self, x_data):
        """
        Calculates the rate of change as the average of the last 500 entries in x_data.
        If there are fewer than 500 entries, it calculates the average for all entries.
        :param x_data: List of frequency changes (x-axis data).
        :return: Average rate of change.
        """
        if len(x_data) < 2:
            return 0.0  # No meaningful rate of change if less than 2 points.

        recent_values = x_data[-500:] if len(x_data) > 500 else x_data
        rate_of_change = sum(abs(recent_values[i] - recent_values[i - 1]) for i in range(1, len(recent_values))) / len(recent_values)
        return rate_of_change

    def start_recording(self):
        # Initialize process in the database
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Process (process_name, start_time) VALUES (?, ?)
                """,
                ("Recording", datetime.now()),
            )
            self.process_id = cursor.lastrowid
            conn.commit()
            logging.info(f"Recording started with process ID: {self.process_id}")
        except sqlite3.Error as e:
            logging.error(f"Failed to start recording: {e}")
        finally:
            conn.close()


    def stop_recording(self):
        # Finalize process and save data
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Process SET end_time = ? WHERE process_id = ?
                """,
                (datetime.now(), self.process_id),
            )
            conn.commit()
            logging.info(f"Recording stopped for process ID: {self.process_id}")
        except sqlite3.Error as e:
            logging.error(f"Failed to stop recording: {e}")
        finally:
            conn.close()
        
        self._save_plot_data(self.x_data, self.y_data)


    def _save_plot_data(self, x_data, y_data):
        if not self.process_id:  # Ensure process_id exists
            logging.error("No process ID available. Cannot save data.")
            return

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            for x, y in zip(x_data, y_data):
                cursor.execute(
                    """
                    INSERT INTO ProcessData (process_id, frequency, frequency_change, frequency_rate_of_change, unit)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (self.process_id, x, 0.0, 0.0, "Hz"),  # Adjust `frequency_change` and `frequency_rate_of_change` as needed
                )
            conn.commit()
            logging.info("Plot data saved to database.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save plot data: {e}")
        finally:
            conn.close()


    def _calculate_rate_of_change(self, x_data):
        """
        Calculates the rate of change as the average of the last 500 entries.
        """
        if len(x_data) < 2:
            return 0.0
        return sum(abs(x_data[i] - x_data[i - 1]) for i in range(1, len(x_data[-500:]))) / min(len(x_data), 500)

    def _initialize_db_connection(self):
        """
        Initializes and returns a database connection.
        """
        try:
            conn = sqlite3.connect("deploy/db/database.db")
            logging.info("Database connection established.")
            return conn
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            raise


    


        
            