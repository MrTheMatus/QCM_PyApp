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
        """Parse incoming data."""
        try:
            # Handle bytes or string input
            if isinstance(line, bytes):
                line = line.decode(Constants.app_encoding)
                
            # Clean the data
            line = line.strip()
            
            # Split and convert to float
            values = [float(x.strip()) for x in line.split(self._split) if x.strip()]
            
            # Send to output queue
            if values:
                self._out_queue.put((time, values))
                
                # If store reference exists, save to file
                if self._store_reference is not None:
                    self._store_reference.add(time, values)
                    
        except ValueError as e:
            logging.warning(f"Could not parse line: {line}, error: {e}")
        except Exception as e:
            logging.error(f"Error processing line: {line}, error: {e}")

