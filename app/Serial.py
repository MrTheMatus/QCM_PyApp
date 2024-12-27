import multiprocessing
from time import time

import serial
from serial.tools import list_ports

from utils.architecture import Architecture
from utils.architecture import OSType
from utils.constants import Constants
import logging
from utils.logdecorator import log_calls, log_all_methods


TAG = "Serial"

@log_all_methods
class SerialProcess(multiprocessing.Process):
    """
    Wrapper for serial package into a multiprocessing instance.
    """
    def __init__(self, parser_process):
        """
        Initialises values for process.
        :param parser_process: Reference to a ParserProcess instance.
        :type parser_process: ParserProcess.
        """
        multiprocessing.Process.__init__(self)
        self._exit = multiprocessing.Event()
        self._parser = parser_process
        self._serial = serial.Serial()
        logging.info(f"{TAG}: Process ready")


    def open(self, port, speed=Constants.serial_default_speed, timeout=Constants.serial_timeout_ms):
        """
        Opens a specified serial port.
        :param port: Serial port name.
        :type port: str.
        :param speed: Baud rate, in bps, to connect to port.
        :type speed: int.
        :param timeout: Sets the general connection timeout.
        :type timeout: float.
        :return: True if the port is available.
        :rtype: bool.
        """
        self._serial.port = port
        self._serial.baudrate = int(speed)
        self._serial.stopbits = serial.STOPBITS_ONE
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.timeout = timeout
        return self._is_port_available(self._serial.port)

    def run(self):
        logging.info("Serial process starting...")
        if self._is_port_available(self._serial.port):
            try:
                self._serial.open()
                logging.info("Serial port opened.")
                timestamp = time()
                while not self._exit.is_set():
                    if self._serial.is_open and self._serial.in_waiting:
                        line = self._serial.readline()
                        logging.warning(f"Raw data read from serial: {line}")
                        if line:
                            try:
                                # Decode and process the line
                                decoded_line = line.decode(Constants.app_encoding).strip()
                                value = float(decoded_line)
                                self._parser.add(time() - timestamp, value)  # Pass as single value
                                logging.warning(f"Serial data received: {value}")
                            except (ValueError, UnicodeDecodeError) as e:
                                logging.error(f"Error processing line: {line}, error: {e}")
            except serial.SerialException as e:
                logging.error(f"Serial error: {e}")
            finally:
                self._serial.close()
                logging.info("Serial process finished.")


    def stop(self):
        """
        Signals the process to stop acquiring data.
        :return:
        """
        logging.info(  "Process finishing...")
        self._exit.set()

    @staticmethod
    def get_ports():
        """
        Gets a list of the available serial ports.
        :return: List of available serial ports.
        :rtype: str list.
        """
        if Architecture.get_os() is OSType.macosx:
            import glob
            return glob.glob("/dev/tty.*")
        else:
            found_ports = []
            for port in list(list_ports.comports()):
                logging.debug("found device")
                found_ports.append(port.device)
            return found_ports

    @staticmethod
    def get_speeds():
        """
        Gets a list of the common serial baud rates, in bps.
        :return: List of the common baud rates, in bps.
        :rtype: str list.
        """
        return [str(v) for v in [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]]

    def _is_port_available(self, port):
        for p in SerialProcess.get_ports():  # Correct call
            if p == port:
                return True
        return False
