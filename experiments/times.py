import time
import csv
import os
from contextlib import ContextDecorator

from loguru import logger

# Dictionary to store execution times
times = {}

# Default folder for storing CSV logs
DEFAULT_FOLDER = "timing_logs"


class timer(ContextDecorator):
    def __init__(self, registry_key):
        self.registry_key = registry_key

    def __enter__(self):
        self.start_time = time.perf_counter()  # High-resolution timer
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_time = time.perf_counter() - self.start_time
        times[self.registry_key] = elapsed_time


def clear_timer(registry_key=None):
    """Clears recorded times. If a registry_key is given, clears only that entry; otherwise, clears all."""
    if registry_key:
        times.pop(registry_key, None)  # Remove specific key if it exists
    else:
        times.clear()  # Clear all recorded times


def save_to_csv(filename="execution_times.csv", folder=DEFAULT_FOLDER):
    """Saves the current state of 'times' dictionary to a CSV file inside a specific folder."""
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Full file path
    filepath = os.path.join(folder, filename)

    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Registry Key", "Execution Time (seconds)"])  # CSV header
        for key, value in times.items():
            writer.writerow([key, value])  # Write each entry

    logger.debug(f"Execution times saved to {filepath}")

