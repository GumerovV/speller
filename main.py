import tkinter as tk
import csv
from keyboard.keyboard_highlight_manager import HighlightManager
from keyboard.keyboard import VirtualKeyboard
from keyboard.keyboard_logger import EventLogger
from bci_client.client import BCIClient


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

    bci_client =  BCIClient('192.168.0.23', 12345)

    highlight_manager = HighlightManager(keyboard, logger, bci_client, interval=100, interval_between_symbols=1000, interval_highlight=1000)

    root.bind('<Return>', lambda event: highlight_manager.start(event=event, root=root))

    root.mainloop()


if __name__ == "__main__":
    main()
