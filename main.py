import tkinter as tk
import csv
from keyboard.keyboard_highlight_manager import HighlightManager
from keyboard.keyboard import VirtualKeyboard
from keyboard.keyboard_logger import EventLogger


def main():
    root = tk.Tk()
    root.title("Виртуальная клавиатура")
    root.configure(bg="black")

    layout = [
        ['A', 'B', 'C', 'D', 'E'],
        ['F', 'G', 'H', 'I', 'J'],
        ['K', 'L', 'M', 'N', 'O'],
        ['P', 'Q', 'R', 'S', 'T'],
        ['U', 'V', 'W', 'X', 'Y'],
    ]

    target_word = "HELLO"

    keyboard = VirtualKeyboard(root, layout, target_word)

    logger = EventLogger(pathname='new_log_file.csv')
    logger.setup()

    highlight_manager = HighlightManager(keyboard, logger, interval=1000, interval_between_symbols=5000, interval_highlight=100)

    root.bind('<Return>', lambda event: highlight_manager.start(event=event, root=root))

    root.mainloop()


if __name__ == "__main__":
    main()
