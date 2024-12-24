import logging
import multiprocessing
import serial
from serial.tools import list_ports
from constants import Constants
from architecture import Architecture, OSType
import time
from time import sleep
import socket
import numpy as np
from logdecorator import log_calls, log_all_methods

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
        """
        Reads the serial port expecting CSV until a stop call is made.
        The expected format is comma (",") separated values, and a new line (CRLF or LF) as a new row.
        While running, it will parse CSV data convert each value to float and added to a queue.
        If incoming data from serial port can't be converted to float, that data will be discarded.
        :return:
        """
        logging.info(  "Process starting...")
        if self._is_port_available(self._serial.port):
            if not self._serial.isOpen():
                self._serial.open()
                logging.info(  "Port opened")
                timestamp = time()
                while not self._exit.is_set():
                    self._parser.add([time() - timestamp, self._serial.readline()])
                logging.info(  "Process finished")
                self._serial.close()
            else:
                logging.warning("Port is not opened")
        else:
                logging.warning("Port is not available")

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
                logging.debug("{}, found device {}".format(TAG, port))
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
        """
        Checks is the port is currently connected to the host.
        :param port: Port name to be verified.
        :return: True if the port is connected to the host.
        :rtype: bool.
        """
        for p in self.get_ports():
            if p == port:
                return True
        return False

TAG = "Simulator"


class SimulatorProcess(multiprocessing.Process):
    """
    Simulates signals and converts them as raw data to feed the processes.
    """
    def __init__(self, parser_process):
        """
        Initialises values for process.
        :param parser_process: Reference to a ParserProcess instance.
        :type parser_process: ParserProcess.
        """
        multiprocessing.Process.__init__(self)
        self._exit = multiprocessing.Event()
        self._period = None
        self._parser = parser_process
        logging.info(f"{TAG}: Process ready")

    def open(self, port=None, speed=Constants.simulator_default_speed, timeout=0.5):
        """
        Opens a specified serial port.
        :param port: Not used.
        :type port: str.
        :param speed: Period of the generated signal.
        :type speed: float.
        :param timeout: Not used.
        :type timeout: float.
        :return: True if the port is available.
        :rtype: bool.
        """
        self._period = float(speed)
        logging.info(  "Using sample rate at {}".format(self._period))
        return True

    def run(self):
        """
        Simulates raw data incoming as CSV.
        :return:
        """
        logging.info(  "Process starting...")
        timestamp = time()
        coef = 2 * np.pi
        while not self._exit.is_set():
            stamp = time() - timestamp
            self._parser.add([stamp, str(("{},{}\r\n".format(np.sin(coef * stamp), np.cos(coef * stamp))))
                             .encode(Constants.app_encoding)])
            sleep(self._period)
        logging.info(  "Process finished")

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
        Gets a list of the available ports.
        :return: List of available ports.
        :rtype: str list.
        """
        return ["Sine Simulator"]

    @staticmethod
    def get_speeds():
        """
        Gets a list of the speeds.
        :return: List of the speeds.
        :rtype: str list.
        """
        return [str(v) for v in [0.002, 0.004, 0.005, 0.010, 0.020, 0.050, 0.100, 0.250]]

TAG = "Socket"


class SocketProcess(multiprocessing.Process):
    """
    Socket client
    """
    def __init__(self, parser_process):
        """
        Initialises values for process.
        :param parser_process: Reference to a ParserProcess instance.
        :type parser_process: ParserProcess
        """
        multiprocessing.Process.__init__(self)
        self._exit = multiprocessing.Event()
        self._parser = parser_process
        self._socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"{TAG}: Process ready")

    def open(self, port='', speed=5555, timeout=0.01):
        """
        Opens a socket connection to specified host and port
        :param port: Host address to connect to.
        :type port: str.
        :param speed: Port number to connect to.
        :type speed: int.
        :param timeout: Sets timeout for socket interactions.
        :type timeout: float.
        :return: True if the connection was open.
        :rtype: bool.
        """
        try:
            #self._socket_client.timeout = timeout
            speed = int(speed)
            self._socket_client.connect((port, speed))
            logging.info(  "Socket open {}:{}".format(port, speed))
            return True
        except socket.timeout:
            logging.warning("Connection timeout")
        return False

    def run(self):
        """
        Reads the socket until a stop call is made.
        :return:
        """
        logging.info(  "Process starting...")
        timestamp = time()

        while not self._exit.is_set():
            stamp = time() - timestamp
            try:
                data = self._socket_client.recv(Constants.SocketClient.buffer_recv_size).decode()
                if len(data) > 0:
                    self._parser.add([stamp, data])
            except socket.timeout:
                logging.warning("read timeout")
        logging.info(  "Process finished")

    def stop(self):
        """
        Signals the process to stop acquiring data.
        :return:
        """
        logging.info(  "Process finishing...")
        self._socket_client.close()
        self._exit.set()

    @staticmethod
    def get_default_host():
        """
        Returns a list of local host names, localhost, host name and local ip address, if available.
        :return: str list.
        """
        values = socket.gethostbyaddr(socket.gethostname())
        hostname = values[0]
        hostip = values[2][0]

        if hostip is not None:
            return [Constants.SocketClient.host_default, hostname, hostip]
        else:
            return [Constants.SocketClient.host_default, hostname]

    @staticmethod
    def get_default_port():
        """
        Returns a list of commonly used socket ports.
        :return: str list.
        """
        return [str(v) for v in Constants.SocketClient.port_default]
TAG = "Worker"
