import csv
import time


class EventLogger:
    """Класс для логирования событий"""

    @staticmethod
    def log_event(row, col, correct):
        timestamp = time.time()
        with open('keyboard_log_oop.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, row, col, correct])
