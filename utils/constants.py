from enum import Enum
from pyqtgraph import AxisItem


class SourceType(Enum):
    """
    Enum for the types of sources. Indices MUST match app_sources constant.
    """
    simulator = 1
    serial = 0
    SocketClient = 2


class Constants:
    """
    Common constants for the application.
    """
    app_title = "RTGraph-openQCM"
    app_version = '0.1'
    app_export_path = "data"
    app_sources = ["Serial", "Simulator", "Socket Client"]
    app_encoding = "utf-8"
    plot_max_lines = 5  # Adjust this number based on your application's requirements



    '''
    TODO 
    custom change: slowing down the update of the timer 
    the QCM data rate is 1 sample/sec 
    '''
    # plot_update_ms = 16
    plot_update_ms = 1000
    plot_xlabel_title = "Time"
    plot_xlabel_unit = "s"
    plot_colors = ['#0072bd', '#d95319', '#edb120', '#7e2f8e', '#77ac30', '#4dbeee', '#a2142f']
    plot_max_lines = len(plot_colors)

    process_join_timeout_ms = 1000

    argument_default_samples = 500

    serial_default_speed = 115200
    serial_timeout_ms = 0.5

    class SocketClient:
        timeout = 0.01
        host_default = "localhost"
        port_default = [5555, 8080, 9090]
        buffer_recv_size = 1024

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

##########################################
#  Provides a non scientific axis notation
##########################################  
# TODO
class NonScientificAxis(AxisItem):
    def __init__(self, *args, **kwargs):
        super(NonScientificAxis, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [int(value*1) for value in values] 