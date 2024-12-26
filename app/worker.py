from multiprocessing import Queue

from utils.constants import Constants, SourceType
from utils.ringBuffer import RingBuffer
from utils import CSVProcess
from utils.Parser import ParserProcess
from app.Serial import SerialProcess
from app.SocketClient import SocketProcess
from app.Simulator import SimulatorProcess
import logging
from utils.logdecorator import log_calls, log_all_methods
import numpy as np


TAG = "Worker"

@log_all_methods
class Worker:
    """
    Concentrates all workers (processes) to run the application.
    """
    def __init__(self, port=None, speed=Constants.serial_default_speed, samples=Constants.argument_default_samples,
                 source=SourceType.serial, export_enabled=False, export_path=Constants.app_export_path, db_path="deploy/db/database.db"):
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
        self._db_process = None  # Database process

        self._port = port
        self._speed = float(speed)
        self._samples = samples
        self._source = source
        self._export = export_enabled
        self._path = export_path
        self._db_path = db_path  # Database path

    def start(self):
        """
        Starts all processes, based on configuration given in constructor.
        :return:
        """
        self.reset_buffers(self._samples)

        if self._export:
            self._csv_process = CSVProcess(path=self._path)
            self._db_process = DatabaseProcess(db_path=self._db_path)
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
            if self._export:
                self._csv_process.start()
                self._db_process.start()
            self._acquisition_process.start()
            self._parser_process.start()
            return True
        else:
            logging.info("Port is not available")
            return False

    def stop(self):
        """
        Stops all running processes.
        :return:
        """
        self.consume_queue()
        for process in [self._acquisition_process, self._parser_process, self._csv_process, self._db_process]:
            if process and process.is_alive():
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
        """Store data in buffers."""
        if not data or len(data) < 2:
            logging.warning(f"Invalid data format: {data}")
            return
            
        timestamp, values = data
        
        if not values:
            logging.warning("No values to store")
            return
            
        # Store timestamp
        self._time_buffer.append(timestamp)
        
        # Store values
        self._store_signal_values(values)
        
        # Log for debugging
        logging.debug(f"Stored values: {values}")

    def _store_signal_values(self, values):
        """Store signal values in buffers"""
        try:
            self._lines = min(len(values), Constants.plot_max_lines)
            for idx in range(self._lines):
                self._data_buffers[idx].append(float(values[idx]))
            logging.debug(f"Stored values: {values[:self._lines]}")
        except (ValueError, IndexError) as e:
            logging.error(f"Error storing values: {e}")

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
        :return:
        """
        self._data_buffers = [RingBuffer(samples) for _ in Constants.plot_colors]
        self._time_buffer = RingBuffer(samples)
        while not self._queue.empty():
            self._queue.get()
        logging.info("Buffers cleared")

    def prepare_plot_data(self):
        """Prepares data for plotting"""
        time_data = np.array(self.get_time_buffer())
        if not time_data.size:
            return None, None, 0
            
        plot_data = []
        for idx in range(self.get_lines()):
            signal_data = np.array(self.get_values_buffer(idx))
            if signal_data.size:
                plot_data.append({
                    'signal': signal_data,
                    'frequency_change': signal_data - signal_data[0] if signal_data.size > 0 else None,
                    'thickness': (signal_data - signal_data[0]) / Constants.density_factor if signal_data.size > 0 else None
                })
                logging.debug(f"Channel {idx} data: {signal_data[-1] if signal_data.size else 'No data'}")
                
        return time_data, plot_data, len(plot_data)
