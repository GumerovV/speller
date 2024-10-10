import tkinter as tk
from keyboard.keyboard_logger import EventLogger

class VirtualKeyboard:
    """Класс для представления виртуальной клавиатуры"""
    def __init__(self, root, layout, target_word):
        self.root = root
        self.layout = layout
        self.target_word = target_word
        self.user_output = ''
        self.current_letter_idx = 0
        self.buttons = []
        self.create_target_word_label()
        self.create_user_output_label()
        self.create_keyboard()

    def create_target_word_label(self):
        self.word_label = tk.Label(self.root, text=self.target_word,
                                   font=('Arial', 24, 'bold'), bg="black", fg="sky blue")
        self.word_label.grid(row=0, column=0, columnspan=len(self.layout[0]))

    def create_user_output_label(self):
        self.user_output_label = tk.Label(self.root, text=self.user_output,
                                   font=('Arial', 24, 'bold'), bg="black", fg="sky blue")
        self.user_output_label.grid(row=1, column=0, columnspan=len(self.layout[0]), pady=10)

    def create_keyboard(self):
        """Создание сетки кнопок (клавиатуры)"""

        for r in range(len(self.layout)):
            row_buttons = []
            for c in range(len(self.layout[0])):
                button = tk.Button(self.root, text=self.layout[r][c], width=5, height=2,
                                   bg="black", fg="sky blue", font=('Arial', 18, 'bold'),
                                   relief=tk.GROOVE)
                button.grid(row=r+15, column=c, padx=5, pady=5)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def clear_highlight(self):
        for r in range(len(self.layout)):
            for c in range(len(self.layout[0])):
                self.buttons[r][c].config(bg="black", fg="sky blue")

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

    def check_letter(self, row=None, col=None, cycle_count=None):
        """Проверка текущего символа и логирование событий"""
        current_letter = self.target_word[self.current_letter_idx]

        if row is not None:  # Проверяем строку
            selected_letters = [self.layout[row][c] for c in range(len(self.layout[0]))]
            if current_letter in selected_letters:
                print(f"Буква '{current_letter}' найдена в строке {row}")
                # if cycle_count == 2:
                #     self.user_output += current_letter
                #     self.user_output_label.config(text=self.user_output)
                #     print(f"Add {current_letter}")
                return True

        if col is not None:  # Проверяем колонку
            selected_letters = [self.layout[r][col] for r in range(len(self.layout))]
            if current_letter in selected_letters:
                print(f"Буква '{current_letter}' найдена в колонке {col}")
                return True

        return False


