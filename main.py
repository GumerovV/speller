import tkinter as tk
import csv
from keyboard.keyboard_highlight_manager import HighlightManager
from keyboard.keyboard import VirtualKeyboard


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

    with open('keyboard_log_oop.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "row", "col", "correct"])

    highlight_manager = HighlightManager(keyboard, interval=100, interval_between_symbols=5000)
    # highlight_manager.start()

    root.bind('<Return>', lambda event: highlight_manager.start(event=event, root=root))

    root.mainloop()


if __name__ == "__main__":
    main()
