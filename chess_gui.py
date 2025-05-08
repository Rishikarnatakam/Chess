import chess as ch
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from ChessEngine import Engine
from PIL import Image, ImageTk

class ChessGUI:
    def __init__(self, root, board):
        self.root = root
        self.board = board

        # Show the color and depth selection dialogs
        self.user_color = self.show_color_selection_dialog()
        if self.user_color is None:
            messagebox.showerror("Error", "No color selected. Exiting game.")
            self.root.destroy()
            return

        self.depth = self.show_depth_selection_dialog()
        if self.depth is None:
            messagebox.showerror("Error", "No depth selected. Exiting game.")
            self.root.destroy()
            return

        # Adjust engine color based on user choice
        self.engine = Engine(self.board, self.depth, ch.BLACK if self.user_color == ch.WHITE else ch.WHITE)
        self.selected_piece = None
        self.piece_images = {}
        self.load_images()

        self.root.title("Chess Game")
        self.canvas = tk.Canvas(root, width=640, height=640)
        self.canvas.pack()

        self.draw_board()  # Draw the board
        self.bind_events()

        if self.engine.color == ch.WHITE:
            self.root.after(500, self.engine_move)  # Ensure engine makes a move if it's White

    def show_color_selection_dialog(self):
        def on_submit():
            color = color_var.get()
            top.destroy()
            return ch.WHITE if color == 'white' else ch.BLACK

        top = tk.Toplevel(self.root)
        top.title("Select Color")

        tk.Label(top, text="Select Color").pack(pady=10)

        color_var = tk.StringVar(value="white")
        tk.Radiobutton(top, text="White", variable=color_var, value="white").pack()
        tk.Radiobutton(top, text="Black", variable=color_var, value="black").pack()

        tk.Button(top, text="Submit", command=on_submit).pack(pady=10)

        # Wait for the user to close the dialog
        self.root.wait_window(top)
        return on_submit()  # Return the selected color

    def show_depth_selection_dialog(self):
        def on_select():
            self.depth = depth_var.get()
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Select Depth")

        tk.Label(top, text="Select Minimax Depth").pack(pady=10)

        depth_var = tk.StringVar(value="2")  # Default to depth 2

        tk.Radiobutton(top, text="Depth 2", variable=depth_var, value="2").pack()
        tk.Radiobutton(top, text="Depth 3", variable=depth_var, value="3").pack()
        tk.Radiobutton(top, text="Depth 4", variable=depth_var, value="4").pack()

        tk.Button(top, text="Submit", command=on_select).pack(pady=10)

        # Wait for the user to select a depth
        self.root.wait_window(top)
        return int(depth_var.get())  # Return the selected depth

    def load_images(self):
        pieces = ['wk', 'wq', 'wr', 'wb', 'wn', 'wp', 'bk', 'bq', 'br', 'bb', 'bn', 'bp']
        for piece in pieces:
            image = Image.open(f'images/{piece}.png')
            image = image.resize((80, 80), Image.LANCZOS)
            self.piece_images[piece] = ImageTk.PhotoImage(image)

    def draw_board(self):
        self.canvas.delete("board")  # Clear previous board to prevent overlaps
        for i in range(8):
            for j in range(8):
                color = "#FFFACD" if (i + j) % 2 == 0 else "#593E1A"
                # Flip board if user is black
                x0 = (j if self.user_color == ch.WHITE else 7-j) * 80
                y0 = (i if self.user_color == ch.WHITE else 7-i) * 80
                self.canvas.create_rectangle(x0, y0, x0 + 80, y0 + 80, fill=color, tags="board")
        self.draw_pieces()

    def draw_pieces(self):
        self.canvas.delete("pieces")  # Clear previous pieces
        for i in range(8):
            for j in range(8):
                piece = self.board.piece_at(ch.square(j, 7 - i))
                if piece is not None:
                    piece_symbol = piece.symbol().lower()
                    color_prefix = 'w' if piece.color == ch.WHITE else 'b'
                    piece_image = self.piece_images[color_prefix + piece_symbol]
                    # Flip board if user is black
                    x = (j if self.user_color == ch.WHITE else 7-j) * 80 + 40
                    y = (i if self.user_color == ch.WHITE else 7-i) * 80 + 40
                    self.canvas.create_image(x, y, image=piece_image, tags="pieces")

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.handle_click)

    def create_move(self, from_square, to_square):
        piece = self.board.piece_at(from_square)
        move = ch.Move(from_square, to_square)

        # Check if it's a pawn promotion move
        if piece.piece_type == ch.PAWN:
            if (self.user_color == ch.WHITE and to_square // 8 == 7) or \
               (self.user_color == ch.BLACK and to_square // 8 == 0):
                promotion_piece = self.show_promotion_dialog()
                return ch.Move(from_square, to_square, promotion=promotion_piece)

        return move

    def show_promotion_dialog(self):
        # Initialize selected_piece with a default value
        selected_piece = 'Queen'
    
        def set_selection():
            nonlocal selected_piece
            selected_piece = promotion_var.get()
            top.destroy()
    
        top = tk.Toplevel(self.root)
        top.title("Pawn Promotion")
    
        tk.Label(top, text="Choose promotion piece:").pack(pady=10)
    
        promotion_var = tk.StringVar(value='Queen')  # Default to Queen
    
        pieces = {
            'Queen': ch.QUEEN,
            'Rook': ch.ROOK,
            'Bishop': ch.BISHOP,
            'Knight': ch.KNIGHT
        }
    
        for piece_name in pieces.keys():
            tk.Radiobutton(top, text=piece_name, variable=promotion_var, value=piece_name).pack(pady=5)
    
        tk.Button(top, text="Submit", command=set_selection).pack(pady=10)
    
        self.root.wait_window(top)
    
        return pieces.get(selected_piece, ch.QUEEN)  # Default to Queen if no valid selection

    def handle_click(self, event):
        col = event.x // 80
        row = event.y // 80
        # Adjust coordinates based on user color
        if self.user_color == ch.BLACK:
            col, row = 7 - col, 7 - row
        square = ch.square(col, 7 - row)
        piece = self.board.piece_at(square)

        if piece is not None and piece.color == self.board.turn and piece.color == self.user_color:
            self.selected_piece = square
            moves = self.board.legal_moves
            legal_moves = [move for move in moves if move.from_square == self.selected_piece]
            self.highlight_squares(legal_moves)
        elif self.selected_piece is not None:
            move = self.create_move(self.selected_piece, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.draw_pieces()
                self.root.after(300, self.engine_move)
            else:
                messagebox.showinfo("Invalid Move", "That move is not legal.")
            self.selected_piece = None
            self.canvas.delete("highlights")
        else:
            messagebox.showinfo("Invalid Move", "Please select your own piece to move.")

    def highlight_squares(self, moves):
        self.canvas.delete("highlights")
        for move in moves:
            col = move.to_square % 8
            row = 7 - move.to_square // 8
            # Adjust coordinates based on user color
            if self.user_color == ch.BLACK:
                col, row = 7 - col, 7 - row
            self.canvas.create_rectangle(col * 80, row * 80, (col + 1) * 80, (row + 1) * 80, 
                                          fill="green",stipple="gray25",outline="", tags="highlights")

    def engine_move(self):
        if not self.board.is_game_over():
            move = self.engine.getBestMove()
            self.board.push(move)
            self.draw_pieces()
            if self.board.is_game_over():
                self.show_game_over_dialog()
        else:
            self.show_game_over_dialog()

    def show_game_over_dialog(self):
        outcome = self.board.outcome()
        if outcome.winner is None:
            # Determine the reason for the draw
            if outcome.termination == ch.Termination.STALEMATE:
                result = "Draw by Stalemate"
            elif outcome.termination == ch.Termination.INSUFFICIENT_MATERIAL:
                result = "Draw by Insufficient Material"
            elif outcome.termination == ch.Termination.FIVEFOLD_REPETITION:
                result = "Draw by Fivefold Repetition"
            elif outcome.termination == ch.Termination.THREEFOLD_REPETITION:
                result = "Draw by Threefold Repetition"
            elif outcome.termination == ch.Termination.FIFTY_MOVES:
                result = "Draw by Fifty Moves"
            else:
                result = "Draw (unknown reason)"
        elif outcome.winner:
            result = "White wins"
        else:
            result = "Black wins"

        messagebox.showinfo("Game Over", f"Game Over: {result}")


if __name__ == "__main__":
    root = tk.Tk()
    board = ch.Board()
    gui = ChessGUI(root, board)
    root.mainloop()
