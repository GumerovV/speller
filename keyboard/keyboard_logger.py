import csv
import datetime
import time


class EventLogger:
    """Класс для логирования событий"""

    def __init__(self, pathname=None):
        self.pathname = pathname if pathname else datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") + '.csv'

    def setup(self):
        with open(self.pathname, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "row", "col", "correct"])

    @staticmethod
    def log_event(pathname, row, col, correct, timestamp):
        with open(pathname, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Логируем строку, если проверяется строка (колонка None)
            if row is not None:
                writer.writerow([timestamp, row, None, correct])

            # Логируем колонку, если проверяется колонка (строка None)
            elif col is not None:
                writer.writerow([timestamp, None, col, correct])
