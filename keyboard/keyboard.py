import tkinter as tk
from keyboard.keyboard_logger import EventLogger

class VirtualKeyboard:
    """Класс для представления виртуальной клавиатуры"""
    def __init__(self, root, layout, target_word):
        self.root = root
        self.layout = layout
        self.target_word = target_word
        self.current_letter_idx = 0
        self.buttons = []
        self.create_keyboard()

    def create_keyboard(self):
        """Создание сетки кнопок (клавиатуры)"""
        for r in range(len(self.layout)):
            row_buttons = []
            for c in range(len(self.layout[0])):
                button = tk.Button(self.root, text=self.layout[r][c], width=5, height=2,
                                   bg="black", fg="sky blue", font=('Arial', 18, 'bold'),
                                   relief=tk.FLAT)
                button.grid(row=r, column=c, padx=5, pady=5)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def highlight(self, row=None, col=None):
        """Подсветка строки или столбца с закругленными белыми областями"""
        # Снятие предыдущей подсветки
        for r in range(len(self.layout)):
            for c in range(len(self.layout[0])):
                self.buttons[r][c].config(bg="black", fg="sky blue")

        if row is not None:
            for c in range(len(self.layout[0])):
                self.buttons[row][c].config(bg="white", fg="black", relief=tk.GROOVE)

        if col is not None:
            for r in range(len(self.layout)):
                self.buttons[r][col].config(bg="white", fg="black", relief=tk.GROOVE)

    def check_letter(self, row, col):
        """Проверка выбранной буквы и логирование события"""
        current_letter = self.target_word[self.current_letter_idx]
        selected_letter = self.layout[row][col]
        correct = (selected_letter == current_letter)

        # Логируем событие
        EventLogger.log_event(row, col, correct)

        # Если выбранная буква правильная, переходим к следующей букве
        if correct:
            self.current_letter_idx += 1
            if self.current_letter_idx >= len(self.target_word):
                print("Слово написано!")
                self.current_letter_idx = 0
                return True
        return False
