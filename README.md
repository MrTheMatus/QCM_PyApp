# AffordableQCM Application

## Overview
This application is designed for real-time monitoring and logging of QCM (Quartz Crystal Microbalance) data. It provides functionality for plotting, database management, and material library handling using a PyQt5-based GUI and an SQLite database for storage.

---

## Setup Instructions

### Prerequisites
- Python 3.7 or higher

### Steps to Set Up
1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate   # On Windows
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Application**:
    ```bash
    python main.py
    ```

---

## Requirements
The dependencies required to run this application are listed in the `requirements.txt` file.

**Example Requirements File**:
```
PyQt5==5.15.7
pyqtgraph==0.13.3
numpy==1.24.3
sqlite3==3.39.2
```

---

## Usage Instructions

1. **Start the Application**:
    Run the command below from the root folder of the project:
    ```bash
    python main.py
    ```

2. **Navigate the UI**:
    - **Materials Management**: Add, update, or delete materials.
    - **Real-Time Plotting**: Monitor frequency and thickness data.
    - **Database Management**: Logs and data are stored in an SQLite database (`app_data.db`).

3. **Optional Command-Line Arguments**:
    Customize the app's behavior using arguments:
    ```bash
    python main.py --debug --samples 1000
    ```
    - `--debug`: Enables debug mode.
    - `--samples`: Number of samples to plot.

---

## Development and Contribution

### Running Tests
To run unit tests, execute the following:
```bash
pytest tests/
```

### Packaging the Application
Use `PyInstaller` to create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

### Logging
Logs are saved to the `data/` directory for debugging and monitoring.

---

## Deployment, Debugging, and Common Issues

### Deployment
- **Packaging the Application**:
  - Use `PyInstaller` to create an executable file:
    ```bash
    pyinstaller --onefile main.py
    ```
  - Distribute the SQLite database (`app_data.db`) pre-initialized if required.

### Debugging
- **Logs**:
  - Runtime logs are stored in the default directory (`data/`) for debugging.
- **Unit Tests**:
  - Run unit tests using `pytest`:
    ```bash
    pytest tests/
    ```

### Common Issues
- **Database Not Found**:
  - Ensure the database (`app_data.db`) is in the correct path or recreated on the first run.
- **Missing Dependencies**:
  - Reinstall required packages:
    ```bash
    pip install -r requirements.txt
    ```

---

## License
This application is open-source and distributed under the GNU General Public License v3.0.
