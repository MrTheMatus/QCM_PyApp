import sqlite3
import matplotlib.pyplot as plt
import numpy as np

class CrystalPlotter:
    def __init__(self, db_path):
        self.db_path = db_path

    def fetch_data(self, process_id=None):
        """
        Fetch frequency and thickness data from the database.
        If process_id is None, fetch all data across all processes.
        """
        query = """
            SELECT timestamp, frequency, thickness 
            FROM ProcessData
        """
        if process_id:
            query += " WHERE process_id = ? ORDER BY timestamp ASC"
        else:
            query += " ORDER BY timestamp ASC"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if process_id:
            cursor.execute(query, (process_id,))
        else:
            cursor.execute(query)

        data = cursor.fetchall()
        conn.close()
        return data

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
