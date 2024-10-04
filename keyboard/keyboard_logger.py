import csv
import time


class EventLogger:
    """Класс для логирования событий"""

    @staticmethod
    def log_event(row, col, correct):
        timestamp = time.time()
        with open('keyboard_log_oop.csv', mode='a', newline='') as file:
            writer = csv.writer(file)

            # Логируем строку, если проверяется строка (колонка None)
            if row is not None:
                writer.writerow([timestamp, row, None, correct])

            # Логируем колонку, если проверяется колонка (строка None)
            elif col is not None:
                writer.writerow([timestamp, None, col, correct])
