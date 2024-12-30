import sys
from PyQt5 import QtWidgets
from controlMainWindow import ControlMainWindow
import logging
import atexit
from PyQt5.QtCore import Qt

logging.info("Logging test - INFO level")
logging.debug("Logging test - DEBUG level")
print("Logging test executed")


def sample_method():
    logging.info("Sample method called")
    print("Sample method executed")

sample_method()

def cleanup_logging():
    logging.shutdown()

atexit.register(cleanup_logging)

# Example: Redirecting sys.settrace logs
def trace_calls(frame, event, arg):
    if event != "call":
        return

    code = frame.f_code
    func_name = code.co_name
    file_name = code.co_filename

    # Exclude specific logs if necessary
    if "eventFilter" in func_name or "eventFilter" in file_name:
        return

    logging.debug(f"Calling {func_name} in {file_name}:{code.co_firstlineno}")
    return trace_calls

# Entry point
if __name__ == "__main__":
    sys.settrace(trace_calls)  # Enable method tracing

    logging.info("Initializing QApplication")
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    app.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)

    logging.info("Initializing ControlMainWindow")
    window = ControlMainWindow()

    logging.info("Showing Main Window")
    window.show()

    logging.info("Entering application event loop")
    sys.exit(app.exec_())

