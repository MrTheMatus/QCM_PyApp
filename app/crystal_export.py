import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import logging
import os
from datetime import datetime
import json
import csv

class CrystalExport:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

    def fetch_data(self, process_id=None, material=None, from_timestamp=None, to_timestamp=None, row_limit=10000):
        query = """
            SELECT 
                ProcessData.process_id, 
                Process.process_name,
                ProcessData.created_at, 
                ProcessData.frequency, 
                ProcessData.frequency_change, 
                ProcessData.thickness,
                SetupConstants.quartz_density,
                SetupConstants.quartz_shear_modulus,
                SetupConstants.quartz_area,
                SetupConstants.tooling_factor,
                SetupConstants.description,
                Process.start_time,
                Process.end_time
            FROM ProcessData
            JOIN Process ON ProcessData.process_id = Process.process_id
            LEFT JOIN SetupConstants ON SetupConstants.id = Process.setup_id
            WHERE 1=1
        """
        params = []

        if process_id:
            query += " AND ProcessData.process_id = ?"
            params.append(process_id)

        if material:
            query += " AND Process.material_name = ?"
            params.append(material)

        if from_timestamp:
            query += " AND ProcessData.created_at >= ?"
            params.append(from_timestamp)

        if to_timestamp:
            query += " AND ProcessData.created_at <= ?"
            params.append(to_timestamp)

        query += f" ORDER BY ProcessData.created_at ASC LIMIT {row_limit}"

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        
        logging.info(f"Fetched data: {results}")

        return [dict(zip(columns, row)) for row in results]


    def plot_data(self, data, color_by_layers=False):
        """
        Generate and display plots for frequency and thickness over time.
        Optionally, color the plot to represent layers on the crystal.
        """
        timestamps, frequencies, thicknesses = zip(*data)

        # Convert timestamps to sequential indices for plotting
        time_indices = np.arange(len(timestamps))

        # Plot frequency over time
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(time_indices, frequencies, label='Frequency (Hz)', color='blue')
        plt.xlabel('Time')
        plt.ylabel('Frequency (Hz)')
        plt.title('Frequency over Time')
        plt.grid(True)
        plt.legend()

        # Plot thickness over time
        plt.subplot(2, 1, 2)
        if color_by_layers:
            # Use a colormap to visualize layers
            cmap = plt.cm.viridis
            norm = plt.Normalize(min(thicknesses), max(thicknesses))
            colors = cmap(norm(thicknesses))
            plt.scatter(time_indices, thicknesses, c=colors, s=10, label='Thickness (nm)', cmap=cmap)
            plt.colorbar(label='Layer Thickness (nm)')
        else:
            plt.plot(time_indices, thicknesses, label='Thickness (nm)', color='green')
        plt.xlabel('Time')
        plt.ylabel('Thickness (nm)')
        plt.title('Thickness over Time')
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.show()

    def estimate_crystal_change_time(self, data, threshold=1000):
        """
        Estimate the time to change the crystal based on a frequency threshold.
        """
        for i, (_, freq, _) in enumerate(data):
            if freq < threshold:
                print(f"Change crystal after {i} time units.")
                break

    # Fetch data directly from the database
    def fetch_data_from_database(conn, process_id, from_timestamp, to_timestamp):
        """Fetch process data from the database."""
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, frequency, frequency_change, thickness
                FROM ProcessData
                WHERE process_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
                """,
                (process_id, from_timestamp, to_timestamp)
            )
            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                logging.info("No data found in the database for the specified range.")
                return None

            return {
                "timestamps": [row[0] for row in rows],
                "frequencies": [row[1] for row in rows],
                "frequency_changes": [row[2] for row in rows],
                "thicknesses": [row[3] for row in rows],
            }
        except sqlite3.Error as e:
            logging.error(f"Database error fetching data for process {process_id}: {e}")
            return None


    def export_to_csv(self, data, output_dir="exports"):
        """
        Exports the provided data to a CSV file with a consistent naming convention.

        Args:
            data (list): List of dictionaries to export.
            output_dir (str): Directory to save the exported CSV file.
        """
        if not data:
            logging.warning("No data to export to CSV.")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate export filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        export_count = len([f for f in os.listdir(output_dir) if f.endswith(".csv")]) + 1
        export_filename = f"data_{current_date}_{export_count}.csv"
        export_path = os.path.join(output_dir, export_filename)

        # Write to CSV
        try:
            with open(export_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            logging.info(f"Data exported to CSV: {export_path}")
        except Exception as e:
            logging.error(f"Failed to export data to CSV: {e}")


    def export_to_json(self, data, output_dir="exports"):
        """
        Exports the provided data to a JSON file with a consistent naming convention.

        Args:
            data (list): List of dictionaries to export.
            output_dir (str): Directory to save the exported JSON file.
        """
        if not data:
            logging.warning("No data to export to JSON.")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate export filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        export_count = len([f for f in os.listdir(output_dir) if f.endswith(".json")]) + 1
        export_filename = f"data_{current_date}_{export_count}.json"
        export_path = os.path.join(output_dir, export_filename)

        # Write to JSON
        try:
            with open(export_path, mode="w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=4)

            logging.info(f"Data exported to JSON: {export_path}")
        except Exception as e:
            logging.error(f"Failed to export data to JSON: {e}")

    def export_to_plot(self, data, process_names, output_dir="exports"):
        """
        Export thickness, frequency, and frequency change to PNG plots.
        Each process is represented as a separate line in the plots.

        Args:
            data (list): List of dictionaries containing the data to plot.
            process_names (dict): Mapping of process_id to process_name.
            output_dir (str): Directory to save the exported plots.
        """
        if not data:
            logging.warning("No data to export to plots.")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Prepare dictionaries for each plot
        plots = {
            "thickness": {"title": "Thickness Over Time", "ylabel": "Thickness (nm)", "data": {}},
            "frequency": {"title": "Frequency Over Time", "ylabel": "Frequency (Hz)", "data": {}},
            "frequency_change": {"title": "Frequency Change Over Time", "ylabel": "Frequency Change (Hz)", "data": {}},
        }

        for row in data:
            try:
                # Parse timestamps from 'created_at' and 'start_time'
                created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S.%f")
                start_time = datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S.%f")

                # Calculate timedelta in seconds
                timedelta_seconds = (created_at - start_time).total_seconds()

                # Get the process_id
                process_id = row.get("process_id")
                if process_id is None:
                    logging.warning(f"Row missing process_id: {row}")
                    continue

                # Initialize data structures for this process_id if not already present
                if process_id not in plots["thickness"]["data"]:
                    plots["thickness"]["data"][process_id] = {"x": [], "y": []}
                    plots["frequency"]["data"][process_id] = {"x": [], "y": []}
                    plots["frequency_change"]["data"][process_id] = {"x": [], "y": []}

                # Append data points to the plots
                plots["thickness"]["data"][process_id]["x"].append(timedelta_seconds)
                plots["thickness"]["data"][process_id]["y"].append(row["thickness"])
                plots["frequency"]["data"][process_id]["x"].append(timedelta_seconds)
                plots["frequency"]["data"][process_id]["y"].append(row["frequency"])
                plots["frequency_change"]["data"][process_id]["x"].append(timedelta_seconds)
                plots["frequency_change"]["data"][process_id]["y"].append(row["frequency_change"])

            except KeyError as e:
                logging.error(f"Missing key in row: {e}. Row: {row}")
            except ValueError as e:
                logging.error(f"Error parsing timestamp: {e}. Row: {row}")
            except Exception as e:
                logging.error(f"Unexpected error processing row: {e}. Row: {row}")

        # Generate plots
        for plot_type, plot_info in plots.items():
            plt.figure(figsize=(10, 6))
            plt.title(plot_info["title"])
            plt.xlabel("Time (seconds)")
            plt.ylabel(plot_info["ylabel"])

            for process_id, line_data in plot_info["data"].items():
                process_name = process_names.get(process_id, f"Process {process_id}")
                plt.plot(line_data["x"], line_data["y"], label=process_name)

            plt.legend()
            plt.grid(True)

            # Generate export filename
            current_date = datetime.now().strftime("%Y-%m-%d")
            export_count = len([f for f in os.listdir(output_dir) if f.startswith(plot_type)]) + 1
            export_filename = f"{plot_type}_{current_date}_{export_count}.png"
            export_path = os.path.join(output_dir, export_filename)

            plt.savefig(export_path)
            plt.close()

            logging.info(f"{plot_type.capitalize()} plot exported to {export_path}")
