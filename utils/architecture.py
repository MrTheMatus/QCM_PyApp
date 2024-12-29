import sys
import platform
import logging
import argparse
from enum import Enum
from pyqtgraph import AxisItem
from utils.logdecorator import log_all_methods

@log_all_methods
class Architecture:
    """
    Wrappers for architecture specific methods.
    """

    @staticmethod
    def get_os():
        """
        Gets the current OS type of the host.
        :return: OS type by OSType enum.
        """
        tmp = str(Architecture.get_os_name())
        if "Linux" in tmp:
            return OSType.linux
        if "Windows" in tmp:
            return OSType.windows
        if "Darwin" in tmp:
            return OSType.macosx
        return OSType.unknown

    @staticmethod
    def get_os_name():
        """
        Gets the current OS name string of the host (as reported by platform).
        :return: OS name.
        :rtype: str.
        """
        return platform.platform()

    @staticmethod
    def get_path():
        """
        Gets the PWD or CWD of the currently running application.
        :return: Path of the PWD or CWD.
        :rtype: str.
        """
        return sys.path[0]

    @staticmethod
    def get_python_version():
        """
        Gets the running Python version (Major, minor, release).
        :return: Python version formatted as major.minor.release.
        :rtype: str.
        """
        version = sys.version_info
        return str("{}.{}.{}".format(version[0], version[1], version[2]))

    @staticmethod
    def is_python_version(major, minor=0):
        """
        Checks if the running Python version is equal or greater than the specified version.
        :param major: Major value of the version.
        :type major: int.
        :param minor: Minor value of the version.
        :type minor: int.
        :return: True if the version specified is equal or greater than the current version.
        :rtype: bool.
        """
        version = sys.version_info
        if version[0] >= major and version[1] >= minor:
            return True
        return False


class OSType(Enum):
    """
    Enum to list OS types.
    """
    unknown = 0
    linux = 1
    macosx = 2
    windows = 3





TAG = "Arguments"


class Arguments:
    """
    Wrapper for argparse package.
    """
    def __init__(self):
        self._parser = None

    def create(self):
        """
        Creates and parses the arguments to be used by the application.
        :return:
        """
        parser = argparse.ArgumentParser(description='RTGraph\nA real time plotting and logging application')
        parser.add_argument("-i", "--info",
                            dest="log_level_info",
                            action='store_true',
                            help="Enable info messages"
                            )

        parser.add_argument("-d", "--debug",
                            dest="log_level_debug",
                            action='store_true',
                            help="Enable debug messages"
                            )

        parser.add_argument("-v", "--verbose",
                            dest="log_to_console",
                            action='store_true',
                            help="Show log messages in console",
                            default=Constants.log_default_console_log
                            )

        parser.add_argument("-s", "--samples",
                            dest="user_samples",
                            default=Constants.argument_default_samples,
                            help="Specify number of sample to show on plot"
                            )
        self._parser = parser.parse_args()

    def set_user_log_level(self):
        """
        Sets the user specified log level.
        :return:
        """
        if self._parser is not None:
            self._parse_log_level()
        else:
            #logging.warning(  "Parser was not created !")
            return None

    def get_user_samples(self):
        """
        Gets the user specified samples to show in the plot.
        :return: Samples specified by user, or default value if not specified.
        :rtype: int.
        """
        return int(self._parser.user_samples)

    def get_user_console_log(self):
        """
        Gets the user specified log to console flag.
        :return: True if log to console is enabled.
        :rtype: bool.
        """
        return self._parser.log_to_console

    def _parse_log_level(self):
        """
        Sets the log level depending on user specification.
        It will also enable or disable log to console based on user specification.
        :return:
        """
        log_to_console = self.get_user_console_log()
        level = logging.INFO
        if self._parser.log_level_info:
            level = logging.INFO
        elif self._parser.log_level_debug:
            level = logging.DEBUG

class SourceType(Enum):
    """
    Enum for the types of sources. Indices MUST match app_sources constant.
    """
    simulator = 1
    serial = 0


class Constants:
    """
    Common constants for the application.
    """
    app_title = "RTGraph-openQCM"
    app_version = '0.1'
    app_export_path = "data"
    app_sources = ["Serial", "Simulator"]
    app_encoding = "utf-8"
    # ...existing code...
    MIN_STORAGE_INTERVAL_MS = 200  # Minimum time between stored measurements
    MIN_FREQUENCY_CHANGE = 0.01    # Minimum frequency change to store

    '''
    TODO 
    custom change: slowing down the update of the timer 
    the QCM data rate is 1 sample/sec 
    '''
    # plot_update_ms = 16
    plot_update_ms = 500
    plot_xlabel_title = "Time"
    plot_xlabel_unit = "s"
    plot_colors = ['#0072bd', '#d95319', '#edb120', '#7e2f8e', '#77ac30', '#4dbeee', '#a2142f']
    plot_max_lines = len(plot_colors)

    process_join_timeout_ms = 1000

    argument_default_samples = 500

    serial_default_speed = 115200
    serial_timeout_ms = 0.5
    simulator_default_speed = 0.002

    csv_default_filename = "%Y-%m-%d_%H-%M-%S"
    csv_delimiter = ","
    csv_extension = "csv"

    parser_timeout_ms = 0.005

    log_filename = "{}.log".format(app_title)
    log_max_bytes = 5120
    log_default_level = 1
    log_default_console_log = False


class MinimalPython:
    """
    Specifies the minimal Python version required.
    """
    major = 3
    minor = 2
    release = 0