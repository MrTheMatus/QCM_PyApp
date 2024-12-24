import multiprocessing
from time import sleep
import logging

TAG = "Parser"

class ParserProcess(multiprocessing.Process):
    """
    Process to parse incoming data and distribute it to the graph and storage queue.
    """
    def __init__(self, data_queue, split=",", consumer_timeout=0.1):
        """
        :param data_queue: Reference to Queue where parsed data will be put.
        :type data_queue: multiprocessing.Queue.
        :param split: Delimiter in incoming data.
        :type split: str.
        :param consumer_timeout: Time to wait after emptying the internal buffer before next parsing.
        :type consumer_timeout: float.
        """
        super().__init__()
        self._exit = multiprocessing.Event()
        self._in_queue = multiprocessing.Queue()
        self._out_queue = data_queue
        self._consumer_timeout = consumer_timeout
        self._split = split
        logging.debug("ParserProcess initialized.")

    def add(self, txt):
        """
        Adds new raw data to the internal buffer.
        :param txt: Raw data coming from the acquisition process.
        :type txt: basestring.
        """
        self._in_queue.put(txt)

    def run(self):
        """
        Main process loop to monitor and parse raw data.
        """
        logging.debug(f"{TAG}: Process starting...")
        while not self._exit.is_set():
            self._consume_queue()
            sleep(self._consumer_timeout)
        self._consume_queue()  # Ensure the queue is emptied before stopping
        logging.debug(f"{TAG}: Process finished.")

    def stop(self):
        """
        Signals the process to stop parsing data.
        """
        logging.debug(f"{TAG}: Process stopping...")
        self._exit.set()

    def _consume_queue(self):
        """
        Consumer method for the queues/process.
        Used in run method to recall after a stop is requested, to ensure queue is emptied.
        :return:
        """
        while not self._in_queue.empty():
            try:
                queue_item = self._in_queue.get(timeout=self._consumer_timeout)
                if queue_item:
                    self._parse_csv(queue_item[0], queue_item[1])
            except Exception as e:
                logging.warning(f"Failed to consume queue: {e}")


    def _parse_data(self, timestamp, line):
        """
        Parses incoming raw data and adds it to the output queue.
        :param timestamp: Timestamp of the data.
        :type timestamp: float.
        :param line: Raw data coming from the acquisition process.
        :type line: basestring.
        """
        if len(line) > 0:
            try:
                if isinstance(line, bytes):
                    values = line.decode("UTF-8").split(self._split)
                elif isinstance(line, str):
                    values = line.split(self._split)
                else:
                    raise TypeError("Unsupported data type for parsing.")

                # Convert to float
                values = [float(v) for v in values]
                logging.debug(f"{TAG}: Parsed values - {values}")

                # Push to the output queue for further processing
                self._out_queue.put((timestamp, values))

            except ValueError:
                logging.warning(f"{TAG}: Can't convert to float. Raw data: {line.strip()}")
            except AttributeError:
                logging.warning(f"{TAG}: Attribute error on type ({type(line)}). Raw data: {line.strip()}")
