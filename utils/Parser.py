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
        while not self._in_queue.empty():
            queue = self._in_queue.get()
            try:
                # Handle incoming data
                if isinstance(queue[1], list):  # If multiple values, iterate
                    values = queue[1]
                else:  # Single value
                    values = [queue[1]]

                self._out_queue.put((queue[0], values))
                logging.debug(f"Parsed and queued values: {values}")
            except Exception as e:
                logging.error(f"Error in parsing: {e}")




    def _parse_csv(self, time, line):
        """Parse incoming data."""
        try:
            # Handle bytes or string input
            if isinstance(line, bytes):
                line = line.decode(Constants.app_encoding)
            
            # Clean the line
            line = line.strip()
            
            if not line:
                return
                
            # Split and convert values
            try:
                # Handle single value case (serial) or multiple values (simulator)
                values = [float(x.strip()) for x in line.split(self._split) if x.strip()]
                if values:
                    self._out_queue.put((time, values))
                    if self._store_reference is not None:
                        self._store_reference.add(time, values)
            except ValueError as e:
                logging.error(f"Error converting values: {line}, error: {e}")
                
        except Exception as e:
            logging.error(f"Error parsing line: {line}, error: {e}")
