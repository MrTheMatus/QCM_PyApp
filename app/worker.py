from multiprocessing import Queue
from utils.constants import Constants, SourceType
from utils.Parser import ParserProcess
from app.Serial import SerialProcess
from app.SocketClient import SocketProcess
from app.Simulator import SimulatorProcess
import logging
import threading
import sqlite3
from utils.ringBuffer import RingBuffer


TAG = "Worker"

class Worker:
    """
    Concentrates all workers (processes) to run the application.
    """
    def __init__(self, port=None, speed=Constants.serial_default_speed, samples=Constants.argument_default_samples, 
                 source=SourceType.serial, export_enabled=False, export_path=Constants.app_export_path):
        self._queue = Queue()
        self._data_buffers = None
        self._time_buffer = None
        self._lock = threading.Lock()
        self._batch_buffer = []
        self._acquisition_process = None
        self._parser_process = None
        self._port = port
        self._speed = speed
        self._samples = samples
        self._source = source
        self._export = export_enabled
        self._path = export_path

    def start(self):
        """
        Starts all processes, based on configuration given in constructor.
        :return:
        """
        self.reset_buffers(self._samples)
        
        # Initialize the parser process without starting it
        if self._export:
            self._parser_process = ParserProcess(self._queue, store_reference=self._csv_process)
        else:
            self._parser_process = ParserProcess(self._queue)

        # Initialize acquisition process based on source
        if self._source == SourceType.serial:
            self._acquisition_process = SerialProcess(self._parser_process)
        elif self._source == SourceType.simulator:
            self._acquisition_process = SimulatorProcess(self._parser_process)
        elif self._source == SourceType.SocketClient:
            self._acquisition_process = SocketProcess(self._parser_process)
        
        # Start the acquisition process
        try:
            if self._acquisition_process.open(port=self._port, speed=self._speed):
                self._acquisition_process.start()
                self._parser_process.start()
                if self._export:
                    self._csv_process.start()
                return True
        except Exception as e:
            logging.error(f"Failed to start processes: {e}")
            return False


    def stop(self):
        """Stops all running processes."""
        self.consume_queue()
        for process in [self._acquisition_process, self._parser_process]:
            if process and process.is_alive():
                process.stop()
                process.join(Constants.process_join_timeout_ms)

    def consume_queue(self):
        """Empties the internal queue and stores the data."""
        while not self._queue.empty():
            self._store_data(self._queue.get(False))

    def _store_data(self, data):
        """Adds data to internal buffers."""
        self._time_buffer.append(data[0])
        self._store_signal_values(data[1])

    def _store_signal_values(self, values):
        """Stores signal values in buffers."""
        for idx in range(min(len(values), len(self._data_buffers))):
            self._data_buffers[idx].append(values[idx])

    def reset_buffers(self, samples):
        """
        Setup/clear the internal buffers.
        :param samples: Number of samples for the buffers.
        :type samples: int
        """
        self._data_buffers = [RingBuffer(samples) for _ in range(Constants.plot_max_lines)]
        self._time_buffer = RingBuffer(samples)
        while not self._queue.empty():
            self._queue.get()
        logging.info("Buffers cleared.")


    def get_time_buffer(self):
        return self._time_buffer.get_all()

    def get_values_buffer(self, idx=0):
        return self._data_buffers[idx].get_all()

    def get_lines(self):
        """
        Gets the current number of lines in the buffers.
        """
        if self._data_buffers is None:
            return 0  # No lines to process
        return len(self._data_buffers or [])


    def is_buffer_full(self, threshold):
        """Check if the time buffer is full."""
        return len(self._time_buffer.get_all()) >= threshold

    def add_data(self, data):
        """Add data to the batch buffer."""
        with self._lock:
            self._batch_buffer.append(data)
            if len(self._batch_buffer) >= 20:  # Write to DB when 20 entries are buffered
                self.flush_to_db()

    def flush_to_db(self):
        """Flush the batch buffer to the database."""
        with self._lock:
            if not self._batch_buffer:
                return
            data_to_save = self._batch_buffer[:]
            self._batch_buffer.clear()

        self._save_to_db(data_to_save)

    def _save_to_db(self, data_batch):
        """Save a batch of data to the database."""
        conn = sqlite3.connect("deploy/db/database.db")
        try:
            cursor = conn.cursor()
            cursor.executemany(
                """INSERT INTO ProcessData (process_id, frequency, frequency_change, frequency_rate_of_change, unit) 
                VALUES (?, ?, ?, ?, ?)""",
                data_batch
            )
            conn.commit()
            logging.info(f"Saved {len(data_batch)} entries to the database.")
        except sqlite3.Error as e:
            logging.error(f"Database save error: {e}")
        finally:
            conn.close()

    @staticmethod
    def get_source_ports(source):
        """Gets the available ports for the given source."""
        if source == SourceType.serial:
            return SerialProcess.get_ports()
        elif source == SourceType.simulator:
            return SimulatorProcess.get_ports()
        elif source == SourceType.SocketClient:
            return SocketProcess.get_default_host()
        else:
            logging.warning("Unknown source selected")
            return None

    @staticmethod
    def get_source_speeds(source):
        """Gets the available speeds for the given source."""
        if source == SourceType.serial:
            return SerialProcess.get_speeds()
        elif source == SourceType.simulator:
            return SimulatorProcess.get_speeds()
        elif source == SourceType.SocketClient:
            return SocketProcess.get_default_port()
        else:
            logging.warning("Unknown source selected")
            return None
        
    def calculate_rate_of_change(self, values):
        """
        Calculate the average rate of change from the last N values.
        """
        if len(values) < 2:
            return 0.0
        return np.mean(np.diff(values[-500:]))


    def calculate_moving_average(self, buffer_idx, window_size):
        """
        Calculate the moving average using the specified buffer.
        """
        return self._data_buffers[buffer_idx].moving_average(window_size)
    
    def is_running(self):
        """
        Checks if the acquisition process is running.
        :return: True if the acquisition process is alive.
        """
        return self._acquisition_process is not None and self._acquisition_process.is_alive()

