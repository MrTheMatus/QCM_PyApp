import os
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import GraphicsLayoutWidget, PlotWidget
import argparse
import platform
import sys
import logging
import logging.handlers
from enum import Enum
import multiprocessing
from time import sleep
from multiprocessing import Queue
from time import time
import serial
from serial.tools import list_ports
import socket
import numpy as np
import csv
import multiprocessing
from time import strftime, gmtime, sleep
from pyqtgraph import AxisItem
import platform
import string
from csv import writer
from datetime import datetime
from os.path import exists as file_exists
import architecture
import CSVProcess
import FileManager
import Logger
import ParserProcess
import PopUp
import RingBuffer
import SerialProcess
import SimulatorProcess
import SocketProcess
import Worker
import Ui 
import ControlWindow


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())

