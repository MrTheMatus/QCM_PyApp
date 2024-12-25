import multiprocessing
from time import sleep
import logging
from utils.constants import Constants

class ParserProcess(multiprocessing.Process):
    def __init__(self, data_queue, store_reference=None,
                 split=Constants.csv_delimiter,
                 consumer_timeout=Constants.parser_timeout_ms):
        super().__init__()
        self._exit = multiprocessing.Event()
        self._in_queue = multiprocessing.Queue()
        self._out_queue = data_queue
        self._consumer_timeout = consumer_timeout
        self._split = split
        self._store_reference = store_reference
        logging.debug("Process ready")

    def add(self, time, line):
        if not line or (isinstance(line, bytes) and line.strip() == b""):
            logging.warning(f"Empty or invalid line received: {line}")
            return
        self._in_queue.put((time, line))


    def run(self):
        """Main loop to consume and parse data."""
        logging.info("Parser process starting...")
        while not self._exit.is_set():
            self._consume_queue()
            sleep(self._consumer_timeout)
        logging.info("Parser process exiting...")

    def stop(self):
        """Signal the process to stop."""
        logging.info("Stopping parser process...")
        self._exit.set()

    def _consume_queue(self):
        """
        Consumer method for the queues/process.
        Used in run method to recall after a stop is requested, to ensure queue is emptied.
        """
        while not self._in_queue.empty():
            try:
                # Fetch data from the queue
                time, line = self._in_queue.get(timeout=self._consumer_timeout)
                # Ensure proper arguments are passed to _parse_csv
                self._parse_csv(time, line)
            except ValueError as ve:
                logging.warning(f"ValueError while consuming queue: {ve}")
            except Exception as e:
                logging.error(f"Error consuming queue item: {e}")



    def _parse_csv(self, time, line):
        """
        Parses incoming data and distributes to external processes.
        :param time: Timestamp.
        :type time: float.
        :param line: Raw data coming from the acquisition process.
        :type line: str or bytes.
        """
        if not line or len(line) == 0:
            logging.warning(f"Empty or invalid line received: {line}")
            return

        try:
            if isinstance(line, bytes):
                values = line.decode("UTF-8").strip().split(self._split)
            elif isinstance(line, str):
                values = line.strip().split(self._split)
            else:
                raise TypeError("Unsupported line type")

            # Convert values to float
            values = [float(v) for v in values if v]
            logging.debug(f"Parsed values: {values}")

            # Push data to the output queue
            self._out_queue.put((time, values))
            if self._store_reference:
                self._store_reference.add(time, values)
        except Exception as e:
            logging.error(f"Error parsing line: {line}. Exception: {e}")

