import sys
from PyQt5 import QtWidgets
from controlMainWindow import ControlMainWindow
from utils.logger import Logger

import logging

# Configure logging
logging.basicConfig(
    filename="log.txt",  # Log file path
    filemode="a",        # Append to the log file
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Set the logging level
)

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

    app = QtWidgets.QApplication(sys.argv)

    # Initialize and show ControlMainWindow directly
    main_window = ControlMainWindow()
    main_window.show()

    sys.exit(app.exec_())
