class HighlightManager:
    """Класс управления подсветкой строк и столбцов"""

    def __init__(self, keyboard, interval=500):
        self.keyboard = keyboard
        self.interval = interval
        self.process = None
        self.highlight_counter = 0  # Счетчик для циклов
        self.cycles = 0  # Подсчитывает, сколько раз цикл повторился
        self.max_cycles = 3  # Ограничиваем до 3 полных циклов строк и столбцов

    def start(self):
        self.highlight_cycle()

    def stop(self):
        if self.process:
            self.keyboard.root.after_cancel(self.process)

    def highlight_cycle(self):
        """Цикл подсветки строк и столбцов"""

        row_count = len(self.keyboard.layout)
        col_count = len(self.keyboard.layout[0])

        print(self.highlight_counter)

        if self.highlight_counter < row_count:  # Подсветка строки
            self.keyboard.highlight(row=self.highlight_counter)
            for c in range(col_count):
                self.keyboard.check_letter(self.highlight_counter, c)

        else:  # Подсветка столбца
            col_index = self.highlight_counter - row_count
            self.keyboard.highlight(col=col_index)
            for r in range(row_count):
                self.keyboard.check_letter(r, col_index)

        self.highlight_counter += 1

        # Если прошли все строки и столбцы, увеличиваем цикл и сбрасываем счётчик
        if self.highlight_counter >= row_count + col_count:
            self.highlight_counter = 0
            self.cycles += 1

        # Проверяем, завершилось ли требуемое количество циклов
        if self.cycles >= self.max_cycles:
            self.stop()
            return

        # Планируем следующий шаг через заданный интервал
        self.process = self.keyboard.root.after(self.interval, self.highlight_cycle)
