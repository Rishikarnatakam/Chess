import chess as ch
import tkinter as tk
from ChessEngine import Engine
from chess_gui import ChessGUI

class Main:
    def __init__(self):
        self.board = ch.Board()

    def start_gui(self):
        root = tk.Tk()
        gui = ChessGUI(root, self.board)
        root.mainloop()

if __name__ == "__main__":
    game = Main()
    game.start_gui()
