import threading
import time
import random

from keyboard.keyboard_logger import EventLogger
from classifier import RandomClassifier


class HighlightManager:
    """Класс управления подсветкой строк и столбцов"""

    def __init__(self, keyboard, logger, bci_client, interval=500, interval_between_symbols=5000, interval_highlight=500):
        self.keyboard = keyboard
        self.logger = logger
        self.bci_client = bci_client
        self.classifier = RandomClassifier()

        self.interval = interval  # ms
        self.interval_between_symbols = interval_between_symbols  # ms
        self.interval_highlight = interval_highlight

        self.process = None
        self.highlight_counter = 0  # Счетчик для циклов
        self.cycles = 0  # Подсчитывает, сколько раз цикл повторился
        self.max_cycles = 3  # Ограничиваем до 3 полных циклов строк и столбцов

        self.eeg_data = []

        self.default_path = [
            [0, None],
            [1, None],
            [2, None],
            [3, None],
            [4, None],
            [None, 0],
            [None, 1],
            [None, 2],
            [None, 3],
            [None, 4],
        ]

        self.probability_mass =  [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        self.shuffled_path = random.sample(self.default_path, len(self.default_path))

    def start(self, event, root):
        self.highlight_cycle_random()
        self.bci_client.connect()
        self.bci_client.start_listening()
        self.start_eeg_polling()  # Запуск опроса данных ЭЭГ
        root.unbind('<Return>')

    def stop(self):
        if self.process:
            self.keyboard.root.after_cancel(self.process)
        self.bci_client.stop_listening()

    def highlight_cycle_random(self):
        """Подсветка в случайном порядке"""
        if self.shuffled_path:
            timestamp = int(time.time() * 1_000_000)

            current_el = self.shuffled_path.pop()
            self.keyboard.highlight(row=current_el[0], col=current_el[1])

            letter_found = self.keyboard.check_letter(row=current_el[0], col=current_el[1], cycle_count=self.cycles)
            EventLogger.log_event(self.logger.pathname, current_el[0], current_el[1], letter_found, timestamp)


            eeg_value = self.bci_client.get_current_eeg()
            print(eeg_value)
            classifier_res = self.classifier.classifiy(eeg_value)
            self.calculate_letters(row=current_el[0], col=current_el[1],value=classifier_res)

        if self.cycles >= self.max_cycles:
            self.cycles = 0
            self.eeg_data = []

            # Добавляем букву
            self.keyboard.user_output += self.get_letter()
            self.keyboard.user_output_label.config(text=self.keyboard.user_output)

            self.keyboard.current_letter_idx += 1
            self.keyboard.clear_highlight()

            self.process = self.keyboard.root.after(self.interval_between_symbols, self.check_end_of_word)
            return

        if not self.shuffled_path:
            self.cycles += 1
            self.shuffled_path = random.sample(self.default_path, len(self.default_path))

        # Планируем следующий шаг через заданный интервал
        self.process = self.keyboard.root.after(self.interval_highlight, self.highlight_pause)

    def highlight_pause(self):
        self.keyboard.clear_highlight()
        self.process = self.keyboard.root.after(self.interval, self.highlight_cycle_random)

    def check_end_of_word(self):
        """Проверка завершения слова и дальнейшие действия"""
        if self.keyboard.current_letter_idx >= len(self.keyboard.target_word):
            self.stop()
        else:
            self.highlight_cycle_random()

    def start_eeg_polling(self):
        """Запуск опроса ЭЭГ данных раз в секунду."""
        self.eeg_polling_thread = threading.Thread(target=self.poll_eeg_data)
        self.eeg_polling_thread.daemon = True
        self.eeg_polling_thread.start()

    def poll_eeg_data(self):
        """Метод опроса данных ЭЭГ раз в секунду."""
        # while True:
        #     eeg_value = self.bci_client.get_current_eeg()  # Получаем данные ЭЭГ от клиента
        #     self.eeg_data.append(eeg_value)  # Добавляем данные ЭЭГ в массив
        #     time.sleep(1.1)  # Пауза 1 секунда
        pass

    def highlight_cycle(self):
        """Цикл подсветки строк и столбцов с проверкой и логированием"""

        row_count = len(self.keyboard.layout)
        col_count = len(self.keyboard.layout[0])

        # Подсветка строки
        if self.highlight_counter < row_count:
            current_row = self.highlight_counter
            self.keyboard.highlight(row=current_row)

            # Проверяем, содержится ли текущая буква в этой строке
            letter_found = any(
                self.keyboard.layout[current_row][c] == self.keyboard.target_word[self.keyboard.current_letter_idx] for
                c in range(col_count))
            self.keyboard.check_letter(row=current_row, cycle_count=self.cycles)
            EventLogger.log_event(self.logger.pathname, current_row, None, letter_found)

        # Подсветка столбца
        elif self.highlight_counter < row_count + col_count:
            current_col = self.highlight_counter - row_count
            self.keyboard.highlight(col=current_col)

            # Проверяем, содержится ли текущая буква в этом столбце
            letter_found = any(
                self.keyboard.layout[r][current_col] == self.keyboard.target_word[self.keyboard.current_letter_idx] for
                r in range(row_count))
            self.keyboard.check_letter(col=current_col, cycle_count=self.cycles)
            EventLogger.log_event(self.logger.pathname, None, current_col, letter_found)

        # Увеличиваем счетчик для подсветки следующей строки или столбца
        self.highlight_counter += 1

        # Если цикл завершился (прошли все строки и столбцы), начинаем новый цикл
        if self.highlight_counter >= row_count + col_count:
            self.highlight_counter = 0
            self.cycles += 1

        # Проверяем, завершилось ли требуемое количество циклов для текущей буквы
        if self.cycles >= self.max_cycles:
            self.cycles = 0
            self.keyboard.current_letter_idx += 1
            time.sleep(10)
            # Проверяем, завершилось ли слово
            if self.keyboard.current_letter_idx >= len(self.keyboard.target_word):
                self.stop()
                return

        # Планируем следующий шаг через заданный интервал
        self.process = self.keyboard.root.after(self.interval, self.highlight_cycle)

    def find_max_element(self):
        max_value = float('-inf')
        max_position = (-1, -1)

        for row_idx, row in enumerate(self.probability_mass):
            for col_idx, value in enumerate(row):
                if value > max_value:
                    max_value = value
                    max_position = (row_idx, col_idx)

        return max_position

    def calculate_letters(self, row = None, col = None, value = None):
        if row is None:
            for r in range(len(self.probability_mass)):
                self.probability_mass[r][col] += value
        else:
            for c in range(len(self.probability_mass[row])):
                self.probability_mass[row][c] += value

    def get_letter(self):
        pos_letter = self.find_max_element()

        self.probability_mass = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        return self.keyboard.layout[pos_letter[0]][pos_letter[1]]



