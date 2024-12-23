from multiprocessing import Queue

from utils.constants import Constants, SourceType
from utils.ringBuffer import RingBuffer
from utils import CSVProcess
from utils.Parser import ParserProcess
from app.Serial import SerialProcess
from app.SocketClient import SocketProcess
from app.Simulator import SimulatorProcess
import logging
import threading
import sqlite3


TAG = "Worker"


class Worker:
    """
    Concentrates all workers (processes) to run the application.
    """
    def __init__(self,
                 port=None,
                 speed=Constants.serial_default_speed,
                 samples=Constants.argument_default_samples,
                 source=SourceType.serial,
                 export_enabled=False,
                 export_path=Constants.app_export_path):
        """
        Creates and orchestrates all processes involved in data acquisition, processing and storing.
        :param port: Port to open on start.
        :type port: str.
        :param speed: Speed for the specified port (depending on source).
        :type speed: float.
        :param samples: Number of samples to keep in the buffers (should match with plot samples).
        :type samples: int.
        :param source: Source type where data should be obtained
        :type source: SourceType.
        :param export_enabled: If true, data will be stored or exported in a file.
        :type export_enabled: bool.
        :param export_path: If specified, defines where the data will be exported.
        :type export_path: str.
        """
        self._queue = Queue()
        self._data_buffers = None
        self._time_buffer = None
        self._lines = 0

        self._acquisition_process = None
        self._parser_process = None
        self._csv_process = None

        self._port = port
        self._speed = float(speed)
        self._samples = samples
        self._source = source
        self._export = export_enabled
        self._path = export_path
        self._batch_buffer = []  # Simple list for buffering data
        self._lock = threading.Lock()  # Ensure thread-safe operations on the buffer

    def start(self):
        """
        Starts all processes, based on configuration given in constructor.
        :return:
        """
        self.reset_buffers(self._samples)
        if self._export:
            self._csv_process = CSVProcess(path=self._path)
            self._parser_process = ParserProcess(self._queue, store_reference=self._csv_process)
        else:
            self._parser_process = ParserProcess(self._queue)

        if self._source == SourceType.serial:
            self._acquisition_process = SerialProcess(self._parser_process)
        elif self._source == SourceType.simulator:
            self._acquisition_process = SimulatorProcess(self._parser_process)
        elif self._source == SourceType.SocketClient:
            self._acquisition_process = SocketProcess(self._parser_process)
        if self._acquisition_process.open(port=self._port, speed=self._speed):
            
            # self._parser_process.start()
            '''
            TypeError: can't pickle weakref objects when running demo in Simulator mode #7
            https://github.com/ssepulveda/RTGraph/issues/7 
            issue for python 3.7 
            this error occurred because self._parser_process.start() is called before self._acquisition_process.start()
            
            '''
            if self._export:
                self._csv_process.start()
            # call first acquisition 
            self._acquisition_process.start() 
            # call after parser 
            self._parser_process.start()
            return True
        else:
            logging.info(  "Port is not available")
            return False

    def stop(self):
        """
        Stops all running processes.
        :return:
        """
        self.consume_queue()
        for process in [self._acquisition_process, self._parser_process, self._csv_process]:
            if process is not None and process.is_alive():
                process.stop()
                process.join(Constants.process_join_timeout_ms)

    def consume_queue(self):
        """
        Empties the internal queue, updating data to consumers.
        :return:
        """
        while not self._queue.empty():
            self._store_data(self._queue.get(False))

    def _store_data(self, data):
        """
        Adds data to internal time and data buffers.
        :param data: values to add to internal buffers.
        :type data: list.
        :return:
        """
        # Add timestamp
        self._time_buffer.append(data[0])
        # Add values
        self._store_signal_values(data[1])

    def _store_signal_values(self, values):
        """
        Stores the signal values in internal buffers.
        :param values: Values to store.
        :type values: float list.
        :return:
        """
        # detect how many lines are present to plot
        size = len(values)
        if self._lines < size:
            if size > Constants.plot_max_lines:
                self._lines = Constants.plot_max_lines
            else:
                self._lines = size

        # store the data in respective buffers
        for idx in range(self._lines):
            self._data_buffers[idx].append(values[idx])

    def get_time_buffer(self):
        """
        Gets the complete buffer for time.
        :return: Time buffer.
        :rtype: float list.
        """
        return self._time_buffer.get_all()

    def get_values_buffer(self, idx=0):
        """
        Gets the complete buffer for a line data, depending on specified index.
        :param idx: Index of the line data to get.
        :type idx: int.
        :return: float list.
        """
        return self._data_buffers[idx].get_all()

    def get_lines(self):
        """
        Gets the current number of found lines in input data.
        :return: Current number of lines.
        :rtype: int.
        """
        return self._lines

    def is_running(self):
        """
        Checks if processes are running.
        :return: True if a process is running.
        :rtype: bool.
        """
        return self._acquisition_process is not None and self._acquisition_process.is_alive()

    @staticmethod
    def get_source_ports(source):
        """
        Gets the available ports for specified source.
        :param source: Source to get available ports.
        :type source: SourceType.
        :return: List of available ports.
        :rtype: str list.
        """
        if source == SourceType.serial:
            return SerialProcess.get_ports()
        elif source == SourceType.simulator:
            return SimulatorProcess.get_ports()
        elif source == SourceType.SocketClient:
            return SocketProcess.get_default_host()
        else:
            logging.warning(  "Unknown source selected")
            return None

    @staticmethod
    def get_source_speeds(source):
        """
        Gets the available speeds for specified source.
        :param source: Source to get available speeds.
        :type source: SourceType.
        :return: List of available speeds.
        :rtype: str list.
        """
        if source == SourceType.serial:
            return SerialProcess.get_speeds()
        elif source == SourceType.simulator:
            return SimulatorProcess.get_speeds()
        elif source == SourceType.SocketClient:
            return SocketProcess.get_default_port()
        else:
            logging.warning(  "Unknown source selected")
            return None

    def reset_buffers(self, samples):
        """
        Setup/clear the internal buffers.
        :param samples: Number of samples for the buffers.
        :type samples: int.
        """
        # Reinitialize data and time buffers
        self._data_buffers = [RingBuffer(samples) for _ in Constants.plot_colors]
        self._time_buffer = RingBuffer(samples)
        
        # Clear the queue
        while not self._queue.empty():
            self._queue.get()
        
        logging.info("Buffers reset and cleared.")


    def get_batch_data(self):
        """
        Fetch the current batch of data for saving to the database.
        Resets the buffers to accumulate new data.
        """
        time_data = self._time_buffer.get_partial()  # Get filled data
        signal_data = [buf.get_partial() for buf in self._data_buffers]
        
        # Clear buffers for new batch
        self.reset_buffers(self._samples)
        
        return time_data, signal_data
    
    def is_buffer_full(self, threshold):
        """
        Check if the buffer has reached the given threshold.
        """
        return self._time_buffer.size >= threshold
    
    def add_data(self, data):
        """Add data to the buffer."""
        with self._lock:
            self._batch_buffer.append(data)
            if len(self._batch_buffer) >= 20:  # Write to DB when 20 entries are buffered
                self.flush_to_db()

    def flush_to_db(self):
        """Flush the buffer to the database."""
        with self._lock:
            if not self._batch_buffer:
                return  # No data to flush
            data_to_save = self._batch_buffer[:]
            self._batch_buffer.clear()

        # Perform the database save operation
        try:
            self._save_to_db(data_to_save)
        except Exception as e:
            logging.error(f"Error saving batch to database: {e}")

    def _save_to_db(self, data_batch):
        """Write a batch of data to the database."""
        conn = sqlite3.connect("your_database_path.db")
        try:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO ProcessData (process_id, timestamp, value)
                VALUES (?, ?, ?)
            """, data_batch)
            conn.commit()
            logging.info(f"Saved {len(data_batch)} entries to the database.")
        finally:
            conn.close()


