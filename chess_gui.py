import chess as ch
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from ChessEngine import Engine
from PIL import Image, ImageTk

class ChessGUI:
    def __init__(self, root, board):
        self.root = root
        self.board = board

        # Configure the main window but don't show it yet
        self.root.title("Chess Game")
        self.root.geometry("1x1+0+0")  # Minimal size, positioned off-screen
        self.root.overrideredirect(True)  # Remove window decorations temporarily

        # Show the combined game configuration dialog
        config_result = self.show_game_configuration_dialog()
        if config_result is None:
            messagebox.showerror("Error", "Game configuration cancelled. Exiting game.")
            self.root.destroy()
            return

        self.user_color, self.depth = config_result

        # Adjust engine color based on user choice
        self.engine = Engine(self.board, self.depth, ch.BLACK if self.user_color == ch.WHITE else ch.WHITE)
        self.selected_piece = None
        self.piece_images = {}
        
        # Move history and navigation system
        self.move_history = []  # List of move data
        self.current_position = 0  # Current position in history (-1 = live game)
        self.game_board = self.board.copy()  # Actual game state
        self.display_board = self.board.copy()  # Board shown to user
        self.is_reviewing = False  # Are we in review mode?
        self.animation_in_progress = False  # Animation lock
        
        self.load_images()

        # Now show the main window properly with navigation panel
        self.root.overrideredirect(False)  # Restore window decorations
        window_width = 900  # 640 for board + 250 for navigation panel + 10 padding
        window_height = 640
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Dynamic window title
        color_name = "White" if self.user_color == ch.WHITE else "Black"
        difficulty_name = self.get_difficulty_name()
        self.root.title("CHESS")
        
        # Center the main window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create main container
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create chess board canvas
        self.canvas = tk.Canvas(self.main_container, width=640, height=640)
        self.canvas.pack(side=tk.LEFT)
        
        # Create navigation panel
        self.create_navigation_panel()

        self.draw_board()  # Draw the board
        self.bind_events()

        if self.engine.color == ch.WHITE:
            self.root.after(500, self.engine_move)  # Ensure engine makes a move if it's White

    def get_difficulty_name(self):
        """Convert depth number to difficulty name"""
        return f"Depth {self.depth}"

    def create_navigation_panel(self):
        """Create the modern right-side navigation panel"""
        self.nav_panel = tk.Frame(self.main_container, width=250, bg="#ffffff", relief=tk.FLAT, bd=0)
        self.nav_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.nav_panel.pack_propagate(False)  # Maintain fixed width
        
        # CHESS Title at the very top in white space
        title_frame = tk.Frame(self.nav_panel, bg="#ffffff", height=55)
        title_frame.pack(fill=tk.X, pady=(10, 5))
        title_frame.pack_propagate(False)
        
        main_title = tk.Label(title_frame, text="CHESS", 
                             font=("Arial", 26), bg="#ffffff", fg="#000000")
        main_title.pack(pady=(12, 8))
        
        # Player Info Section
        player_frame = tk.Frame(self.nav_panel, bg="#eff6ff", relief=tk.FLAT, bd=1)
        player_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        # Player info without icons (cleaner look)
        player_color_name = "White" if self.user_color == ch.WHITE else "Black"
        engine_color_name = "Black" if self.user_color == ch.WHITE else "White"
        
        player_info = tk.Label(player_frame, text=f"You: {player_color_name}  vs  Engine", 
                              font=("Arial", 11, "bold"), bg="#eff6ff", fg="#1e40af")
        player_info.pack(pady=(8, 4))
        
        difficulty_icons = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
        difficulty_icon = difficulty_icons.get(self.get_difficulty_name(), "⚪")
        difficulty_info = tk.Label(player_frame, 
                                  text=f"Difficulty: {difficulty_icon} {self.get_difficulty_name()} (Depth {self.depth})", 
                                  font=("Arial", 10), bg="#eff6ff", fg="#64748b")
        difficulty_info.pack(pady=(0, 8))
        
        # Move History Section
        history_frame = tk.Frame(self.nav_panel, bg="#f8fafc", relief=tk.FLAT, bd=1)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        history_header = tk.Label(history_frame, text="📜 Move History", 
                                 font=("Arial", 11, "bold"), bg="#f8fafc", fg="#374151")
        history_header.pack(pady=(8, 8))
        
        # Scrollable move list with modern styling
        list_container = tk.Frame(history_frame, bg="#f8fafc")
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        self.move_listbox = tk.Listbox(list_container, 
                                      font=("Consolas", 9), 
                                      selectmode=tk.SINGLE,
                                      bg="white",
                                      fg="#374151",
                                      selectbackground="#3b82f6",
                                      selectforeground="white",
                                      relief=tk.FLAT,
                                      bd=1,
                                      highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.move_listbox.yview)
        self.move_listbox.config(yscrollcommand=scrollbar.set)
        
        self.move_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind listbox selection
        self.move_listbox.bind('<<ListboxSelect>>', self.on_move_select)
        
        # Navigation Controls Section (MOVED HERE - after history)
        nav_frame = tk.Frame(self.nav_panel, bg="#ffffff", relief=tk.FLAT, bd=1)
        nav_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        nav_title = tk.Label(nav_frame, text="Navigation", 
                            font=("Arial", 9, "bold"), bg="#ffffff", fg="#6b7280")
        nav_title.pack(pady=(8, 4))
        
        # Compact navigation buttons in single row using grid for perfect alignment
        nav_btn_container = tk.Frame(nav_frame, bg="#ffffff")
        nav_btn_container.pack(pady=(0, 8))
        
        nav_btn_frame = tk.Frame(nav_btn_container, bg="#ffffff")
        nav_btn_frame.pack()
        
        # Style for navigation buttons - consistent sizing
        btn_style = {
            "font": ("Arial", 12),
            "width": 4,
            "height": 2,
            "relief": tk.FLAT,
            "bd": 1,
            "bg": "#e5e7eb",
            "fg": "#374151",
            "activebackground": "#3b82f6",
            "activeforeground": "white"
        }
        
        # Use grid layout for perfect alignment - clean 4-button design
        self.first_btn = tk.Button(nav_btn_frame, text="⏮", command=self.go_to_first, **btn_style)
        self.first_btn.grid(row=0, column=0, padx=4, pady=2, sticky="nsew")
        
        self.prev_btn = tk.Button(nav_btn_frame, text="⏪", command=self.go_to_previous, **btn_style)
        self.prev_btn.grid(row=0, column=1, padx=4, pady=2, sticky="nsew")
        
        self.next_btn = tk.Button(nav_btn_frame, text="⏩", command=self.go_to_next, **btn_style)
        self.next_btn.grid(row=0, column=2, padx=4, pady=2, sticky="nsew")
        
        self.last_btn = tk.Button(nav_btn_frame, text="⏭", command=self.go_to_last, **btn_style)
        self.last_btn.grid(row=0, column=3, padx=4, pady=2, sticky="nsew")
        
        # Configure grid columns to be uniform - 4 buttons with better spacing
        for i in range(4):
            nav_btn_frame.columnconfigure(i, weight=1, uniform="button")
        
        # Action Buttons Section (at bottom)
        action_frame = tk.Frame(self.nav_panel, bg="#ffffff")
        action_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        # Modern action buttons
        self.new_game_btn = tk.Button(action_frame, text="🎮 New Game", 
                                     command=self.new_game, 
                                     font=("Arial", 10, "bold"),
                                     bg="#10b981", fg="white", 
                                     relief=tk.FLAT, bd=0, height=2,
                                     activebackground="#059669",
                                     activeforeground="white")
        self.new_game_btn.pack(fill=tk.X, pady=(0, 4))
        
        self.export_btn = tk.Button(action_frame, text="💾 Export PGN", 
                                   command=self.export_pgn, 
                                   font=("Arial", 10),
                                   bg="#3b82f6", fg="white",
                                   relief=tk.FLAT, bd=0, height=2,
                                   activebackground="#2563eb",
                                   activeforeground="white")
        self.export_btn.pack(fill=tk.X)
        
        # Apply consistent backgrounds to prevent white boxes
        self.apply_consistent_backgrounds()

    def update_navigation_state(self):
        """Update navigation button states"""
        total_moves = len(self.move_history)
        
        if self.is_reviewing and total_moves > 0:
            # Enable/disable buttons based on position
            self.first_btn.config(state=tk.NORMAL if self.current_position > 0 else tk.DISABLED)
            self.prev_btn.config(state=tk.NORMAL if self.current_position > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_position < total_moves - 1 else tk.DISABLED)
            self.last_btn.config(state=tk.NORMAL if self.current_position < total_moves - 1 else tk.DISABLED)
        else:
            # Disable navigation buttons appropriately in live game
            self.first_btn.config(state=tk.NORMAL if total_moves > 0 else tk.DISABLED)
            self.prev_btn.config(state=tk.NORMAL if total_moves > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)  # Can't go forward in live game
            self.last_btn.config(state=tk.DISABLED)  # Already at last in live game

    def add_move_to_history(self, move, notation=None):
        """Add a move to the history"""
        if notation is None:
            # Generate notation BEFORE applying the move to avoid board state issues
            notation = self.board.san(move)
        
        move_data = {
            'move': move,
            'notation': notation,
            'fen': self.board.fen()  # Store FEN before the move
        }
        
        self.move_history.append(move_data)
        self.current_position = len(self.move_history) - 1
        
        # Update move list with paired notation (1. e4 e5, 2. Nf3 Bb4)
        self.update_move_list()
        
        self.update_navigation_state()

    def update_move_list(self):
        """Update the move list display with paired moves"""
        self.move_listbox.delete(0, tk.END)
        
        i = 0
        while i < len(self.move_history):
            move_num = (i // 2) + 1
            white_move = self.move_history[i]['notation'] if i < len(self.move_history) else ""
            black_move = self.move_history[i + 1]['notation'] if i + 1 < len(self.move_history) else ""
            
            if black_move:
                # Both white and black moves
                display_text = f"{move_num}. {white_move} {black_move}"
            else:
                # Only white move
                display_text = f"{move_num}. {white_move}"
            
            self.move_listbox.insert(tk.END, display_text)
            i += 2
        
        # Scroll to bottom and highlight current position if reviewing
        self.move_listbox.see(tk.END)
        if self.is_reviewing:
            self.highlight_current_move()

    # Navigation methods
    def go_to_first(self):
        """Go to the first move"""
        if self.move_history:
            self.current_position = 0
            self.is_reviewing = True
            self.show_position(self.current_position)
            
    def go_to_previous(self):
        """Go to the previous move"""
        if self.current_position > 0:
            self.current_position -= 1
            self.is_reviewing = True
            self.show_position(self.current_position)
            
    def go_to_next(self):
        """Go to the next move"""
        if self.current_position < len(self.move_history) - 1:
            self.current_position += 1
            # Check if we've reached the last position (live game)
            if self.current_position == len(self.move_history) - 1:
                # We're at the last move, go directly to live mode (skip show_position to avoid double-update)
                self.go_to_last()
            else:
                # Still in review mode, show the position normally
                self.show_position(self.current_position)
        else:
            # We're already at the last move, so exit review mode
            self.go_to_last()
            
    def go_to_last(self):
        """Go to the last move (live game)"""
        if self.move_history:
            self.current_position = len(self.move_history) - 1
            
            # Properly synchronize board state when returning to live mode
            # Rebuild the main board from move history to ensure consistency
            self.board = ch.Board()
            for move_data in self.move_history:
                self.board.push(move_data['move'])
            
            # Sync display board with main board
            self.display_board = self.board.copy()
            
            # Exit review mode
            self.is_reviewing = False
            
            # Update display
            self.draw_pieces()
            self.highlight_current_move()
            
            # Check if it's the engine's turn and trigger engine move
            if (self.board.turn != self.user_color and 
                not self.board.is_game_over()):
                self.root.after(500, self.engine_move)
            
        self.update_navigation_state()
            
    def show_position(self, position):
        """Display the board at a specific position in history"""
        if 0 <= position < len(self.move_history):
            # Create board state up to this position
            temp_board = ch.Board()
            for i in range(position + 1):
                temp_board.push(self.move_history[i]['move'])
            
            self.display_board = temp_board.copy()
            self.draw_pieces()
            
            # Highlight the current move in paired list
            self.highlight_current_move()
            
        self.update_navigation_state()

    def highlight_current_move(self):
        """Highlight the current move in the paired move list"""
        if self.move_history and self.is_reviewing:
            # Calculate which line contains the current move
            line_index = self.current_position // 2
            self.move_listbox.selection_clear(0, tk.END)
            if line_index < self.move_listbox.size():
                self.move_listbox.selection_set(line_index)
                self.move_listbox.see(line_index)


        
    def on_move_select(self, event):
        """Handle move selection from listbox with paired moves"""
        selection = self.move_listbox.curselection()
        if selection and self.move_history:
            line_index = selection[0]
            # Convert line index to move position (each line has 2 moves)
            move_position = (line_index * 2) + 1  # +1 to get the black move of that pair by default
            
            # If we're at the last line and it only has white move, adjust
            if move_position >= len(self.move_history):
                move_position = len(self.move_history) - 1
            
            self.current_position = move_position
            self.is_reviewing = True
            self.show_position(move_position)

    def new_game(self):
        """Start a new game"""
        result = messagebox.askyesno("New Game", "Start a new game? Current game will be lost.")
        if result:
            # Reset all game state
            self.game_board = ch.Board()
            self.display_board = ch.Board()
            self.board = ch.Board()  # Reset the main board too
            self.move_history = []
            self.current_position = 0
            self.is_reviewing = False
            self.selected_piece = None
            
            # Clear move listbox
            self.move_listbox.delete(0, tk.END)
            
            # Redraw board
            self.draw_board()
            self.update_navigation_state()
            
            # Restart engine move if needed
            if self.engine.color == ch.WHITE:
                self.root.after(500, self.engine_move)
                
    def export_pgn(self):
        """Export game to PGN format"""
        if not self.move_history:
            messagebox.showinfo("Export PGN", "No moves to export!")
            return
            
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".pgn",
                filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
            )
            
            if filename:
                # Determine game result
                result_pgn = "*"
                result_text = "Game in progress"
                
                if self.board.is_game_over():
                    outcome = self.board.outcome()
                    if outcome.winner is None:
                        result_pgn = "1/2-1/2"
                        if outcome.termination == ch.Termination.STALEMATE:
                            result_text = "1/2-1/2 (Draw by Stalemate)"
                        elif outcome.termination == ch.Termination.INSUFFICIENT_MATERIAL:
                            result_text = "1/2-1/2 (Draw by Insufficient Material)"
                        elif outcome.termination == ch.Termination.FIVEFOLD_REPETITION:
                            result_text = "1/2-1/2 (Draw by Fivefold Repetition)"
                        elif outcome.termination == ch.Termination.THREEFOLD_REPETITION:
                            result_text = "1/2-1/2 (Draw by Threefold Repetition)"
                        elif outcome.termination == ch.Termination.FIFTY_MOVES:
                            result_text = "1/2-1/2 (Draw by Fifty Moves)"
                        else:
                            result_text = "1/2-1/2 (Draw)"
                    elif outcome.winner == ch.WHITE:
                        result_pgn = "1-0"
                        result_text = "1-0 (White wins)"
                    else:
                        result_pgn = "0-1"
                        result_text = "0-1 (Black wins)"
                
                with open(filename, 'w') as f:
                    # Write PGN headers (removed Event, Site, Date)
                    f.write(f'[White "{"Human" if self.user_color == ch.WHITE else "Engine"}"]\n')
                    f.write(f'[Black "{"Human" if self.user_color == ch.BLACK else "Engine"}"]\n')
                    f.write(f'[Result "{result_pgn}"]\n\n')
                    
                    # Write moves
                    move_text = ""
                    for i, move_data in enumerate(self.move_history):
                        if i % 2 == 0:  # White move
                            move_num = (i // 2) + 1
                            move_text += f"{move_num}. {move_data['notation']} "
                        else:  # Black move
                            move_text += f"{move_data['notation']} "
                    
                    f.write(move_text + result_pgn + "\n")
                    
                messagebox.showinfo("Export PGN", f"Game exported to {filename}\nResult: {result_text}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def show_game_configuration_dialog(self):
        result = None
        
        def on_start_game():
            nonlocal result
            color = ch.WHITE if color_var.get() == 'white' else ch.BLACK
            depth = int(depth_var.get())
            result = (color, depth)
            top.destroy()
        
        def on_cancel():
            nonlocal result
            result = None
            top.destroy()

        # Create the dialog window
        top = tk.Toplevel(self.root)
        top.title("Game Configuration")
        top.resizable(False, False)
        
        # Center the dialog on screen with improved sizing
        dialog_width = 450
        dialog_height = 485
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        top.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        top.minsize(450, 485)  # Ensure minimum size
        
        # Make dialog modal and ensure it appears on top
        top.transient(self.root)
        top.grab_set()
        top.focus_force()
        top.lift()
        top.attributes('-topmost', True)
        
        # Main frame with padding
        main_frame = tk.Frame(top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title with larger font
        title_label = tk.Label(main_frame, text="Game Configuration", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Color selection frame with better styling
        color_frame = tk.LabelFrame(main_frame, text="Choose Your Color", 
                                   font=("Arial", 12, "bold"), padx=15, pady=12)
        color_frame.pack(fill=tk.X, pady=(0, 15))

        color_var = tk.StringVar(value="white")
        tk.Radiobutton(color_frame, text="White", variable=color_var, 
                      value="white", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        tk.Radiobutton(color_frame, text="Black", variable=color_var, 
                      value="black", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        
        # Engine depth selection frame with better styling
        depth_frame = tk.LabelFrame(main_frame, text="Choose Engine Depth", 
                                   font=("Arial", 12, "bold"), padx=15, pady=12)
        depth_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Depth selection label and dropdown
        depth_label = tk.Label(depth_frame, text="Engine Depth:", font=("Arial", 11))
        depth_label.pack(anchor=tk.W, pady=(0, 5))
        
        depth_var = tk.StringVar(value="3")
        depth_dropdown = ttk.Combobox(depth_frame, textvariable=depth_var, 
                                     values=["2", "3", "4", "5", "6", "7"],
                                     state="readonly", font=("Arial", 11), width=10)
        depth_dropdown.pack(anchor=tk.W, pady=(0, 5))
        depth_dropdown.set("3")  # Default to depth 3
        
        # Button frame with proper spacing to ensure visibility
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 10))
        
        # Enhanced buttons with better sizing
        cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel, 
                              font=("Arial", 12), width=12, height=2,
                              relief=tk.RAISED, bd=2)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        start_btn = tk.Button(button_frame, text="Start Game", command=on_start_game, 
                             font=("Arial", 12, "bold"), width=14, height=2, 
                             bg="#4CAF50", fg="white", activebackground="#45a049",
                             relief=tk.RAISED, bd=2)
        start_btn.pack(side=tk.RIGHT)
        
        # Handle window close button
        top.protocol("WM_DELETE_WINDOW", on_cancel)
        
        # Wait for the user to make a selection
        self.root.wait_window(top)
        return result

    def load_images(self):
        pieces = ['wk', 'wq', 'wr', 'wb', 'wn', 'wp', 'bk', 'bq', 'br', 'bb', 'bn', 'bp']
        for piece in pieces:
            image = Image.open(f'images/{piece}.png')
            image = image.resize((80, 80), Image.LANCZOS)
            self.piece_images[piece] = ImageTk.PhotoImage(image)

    def draw_board(self):
        self.canvas.delete("board")  # Clear previous board to prevent overlaps
        self.canvas.delete("coordinates")  # Clear previous coordinates
        
        for i in range(8):
            for j in range(8):
                color = "#FFFACD" if (i + j) % 2 == 0 else "#593E1A"
                # Flip board if user is black
                x0 = (j if self.user_color == ch.WHITE else 7-j) * 80
                y0 = (i if self.user_color == ch.WHITE else 7-i) * 80
                self.canvas.create_rectangle(x0, y0, x0 + 80, y0 + 80, fill=color, tags="board")
                
                # Add coordinates
                text_color = "#333333" if (i + j) % 2 == 0 else "#CCCCCC"
                
                # Add file letters (a-h) on bottom row only
                if (self.user_color == ch.WHITE and i == 7) or (self.user_color == ch.BLACK and i == 0):
                    if self.user_color == ch.WHITE:
                        file_letter = chr(ord('a') + j)
                    else:
                        # When playing as Black, show files h-a from left to right
                        actual_j = 7 - j  # Get the actual file index before flipping
                        file_letter = chr(ord('h') - actual_j)
                    # Bottom-right corner of square (moved closer to corner)
                    self.canvas.create_text(x0 + 72, y0 + 75, text=file_letter, 
                                          font=("Arial", 8, "bold"), fill=text_color, tags="coordinates")
                
                # Add rank numbers (1-8) on leftmost column only
                if (self.user_color == ch.WHITE and j == 0) or (self.user_color == ch.BLACK and j == 7):
                    if self.user_color == ch.WHITE:
                        rank_number = str(8 - i)
                    else:
                        # When playing as Black, show ranks 8-1 from bottom to top
                        actual_i = 7 - i  # Get the actual rank index before flipping
                        rank_number = str(actual_i + 1)
                    # Top-left corner of square (moved closer to corner)
                    self.canvas.create_text(x0 + 8, y0 + 12, text=rank_number, 
                                          font=("Arial", 8, "bold"), fill=text_color, tags="coordinates")
        
        self.draw_pieces()

    def draw_pieces(self, exclude_square=None):
        """Draw pieces on the board, optionally excluding one square"""
        self.canvas.delete("pieces")  # Clear previous pieces
        
        # Use display_board for showing positions during review
        board_to_display = self.display_board if self.is_reviewing else self.board
        
        for i in range(8):
            for j in range(8):
                square = ch.square(j, 7 - i)
                if exclude_square is not None and square == exclude_square:
                    continue  # Skip this square (for animation)
                    
                piece = board_to_display.piece_at(square)
                if piece is not None:
                    piece_symbol = piece.symbol().lower()
                    color_prefix = 'w' if piece.color == ch.WHITE else 'b'
                    piece_image = self.piece_images[color_prefix + piece_symbol]
                    # Flip board if user is black
                    x = (j if self.user_color == ch.WHITE else 7-j) * 80 + 40
                    y = (i if self.user_color == ch.WHITE else 7-i) * 80 + 40
                    self.canvas.create_image(x, y, image=piece_image, tags="pieces")

    def animate_move(self, from_square, to_square, move, duration=250, callback=None):
        """Animate a piece moving from one square to another"""
        if self.animation_in_progress:
            return
            
        self.animation_in_progress = True
        
        # Get piece at from_square
        piece = self.board.piece_at(from_square)
        if piece is None:
            self.animation_in_progress = False
            if callback:
                callback()
            return
        
        # Generate notation BEFORE making the move to avoid board state issues
        notation = self.board.san(move)
        
        # Calculate positions
        from_file, from_rank = from_square % 8, 7 - from_square // 8
        to_file, to_rank = to_square % 8, 7 - to_square // 8
        
        # Flip coordinates if user is black
        if self.user_color == ch.BLACK:
            from_file, from_rank = 7 - from_file, 7 - from_rank
            to_file, to_rank = 7 - to_file, 7 - to_rank
        
        start_x = from_file * 80 + 40
        start_y = from_rank * 80 + 40
        end_x = to_file * 80 + 40
        end_y = to_rank * 80 + 40
        
        # Create piece image for animation
        piece_symbol = piece.symbol().lower()
        color_prefix = 'w' if piece.color == ch.WHITE else 'b'
        piece_image = self.piece_images[color_prefix + piece_symbol]
        
        # Draw board without the moving piece
        self.draw_pieces(exclude_square=from_square)
        
        # Create animated piece
        animated_piece = self.canvas.create_image(start_x, start_y, image=piece_image, tags="animation")
        
        # Animation parameters
        steps = 20
        step_duration = duration // steps
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        def animate_step(step):
            if step <= steps:
                current_x = start_x + dx * step
                current_y = start_y + dy * step
                self.canvas.coords(animated_piece, current_x, current_y)
                
                if step < steps:
                    self.root.after(step_duration, lambda: animate_step(step + 1))
                else:
                    # Animation complete - execute the move
                    self.canvas.delete("animation")
                    self.animation_in_progress = False
                    
                    # Execute the actual move on both boards
                    self.board.push(move)
                    self.game_board = self.board.copy()  # Keep boards in sync
                    
                    # Add to history with pre-generated notation
                    self.add_move_to_history(move, notation)
                    
                    # Redraw pieces
                    self.draw_pieces()
                    
                    if callback:
                        callback()
        
        animate_step(0)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.handle_click)
        # Add keyboard navigation
        self.root.bind("<Left>", lambda e: self.go_to_previous())
        self.root.bind("<Right>", lambda e: self.go_to_next())
        self.root.bind("<Home>", lambda e: self.go_to_first())
        self.root.bind("<End>", lambda e: self.go_to_last())
        self.root.focus_set()  # Enable keyboard events
        
        # Bind window resize to maintain backgrounds
        self.root.bind("<Configure>", lambda e: self.apply_consistent_backgrounds() if e.widget == self.root else None)

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
        selected_piece = 'Queen'
        result = ch.QUEEN
    
        def select_piece(piece_name):
            nonlocal selected_piece, result
            selected_piece = piece_name
            result = pieces[piece_name]
            # Highlight selected card
            for card in piece_cards:
                if card['name'] == piece_name:
                    card['frame'].config(bg="#3b82f6", relief=tk.RAISED)
                    card['label'].config(bg="#3b82f6", fg="white")
                else:
                    card['frame'].config(bg="#f8fafc", relief=tk.FLAT)
                    card['label'].config(bg="#f8fafc", fg="#374151")
        
        def confirm_selection():
            top.destroy()
        
        def cancel_selection():
            nonlocal result
            result = ch.QUEEN  # Default fallback
            top.destroy()
    
        # Create modern promotion dialog
        top = tk.Toplevel(self.root)
        top.title("Pawn Promotion")
        top.resizable(False, False)
        top.configure(bg="#ffffff")
        
        # Center the dialog relative to main window
        dialog_width = 450
        dialog_height = 250
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        x = main_x + (main_width - dialog_width) // 2
        y = main_y + (main_height - dialog_height) // 2
        top.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal
        top.transient(self.root)
        top.grab_set()
        top.focus_force()
        
        # Header
        header_frame = tk.Frame(top, bg="#1e40af", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text="🏁 Pawn Promotion", 
                               font=("Arial", 16, "bold"), bg="#1e40af", fg="white")
        header_label.pack(expand=True)
        
        # Main content
        content_frame = tk.Frame(top, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        instruction_label = tk.Label(content_frame, text="Choose your promotion piece:", 
                                    font=("Arial", 12), bg="#ffffff", fg="#374151")
        instruction_label.pack(pady=(0, 15))
        
        # Piece selection cards
        pieces_frame = tk.Frame(content_frame, bg="#ffffff")
        pieces_frame.pack(pady=(0, 20))
        
        pieces = {
            'Queen': ch.QUEEN,
            'Rook': ch.ROOK,
            'Bishop': ch.BISHOP,
            'Knight': ch.KNIGHT
        }
        
        piece_symbols = {
            'Queen': '♕' if self.user_color == ch.WHITE else '♛',
            'Rook': '♖' if self.user_color == ch.WHITE else '♜',
            'Bishop': '♗' if self.user_color == ch.WHITE else '♝',
            'Knight': '♘' if self.user_color == ch.WHITE else '♞'
        }
        
        piece_cards = []
        
        for i, (piece_name, piece_type) in enumerate(pieces.items()):
            # Create card frame
            card_frame = tk.Frame(pieces_frame, bg="#f8fafc", relief=tk.FLAT, 
                                 bd=2, cursor="hand2")
            card_frame.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            
            # Piece symbol
            symbol_label = tk.Label(card_frame, text=piece_symbols[piece_name], 
                                   font=("Arial", 24), bg="#f8fafc", fg="#374151")
            symbol_label.pack(pady=(10, 5))
            
            # Piece name
            name_label = tk.Label(card_frame, text=piece_name, 
                                 font=("Arial", 10, "bold"), bg="#f8fafc", fg="#374151")
            name_label.pack(pady=(0, 10))
            
            # Make card clickable
            for widget in [card_frame, symbol_label, name_label]:
                widget.bind("<Button-1>", lambda e, name=piece_name: select_piece(name))
            
            piece_cards.append({
                'name': piece_name,
                'frame': card_frame,
                'label': name_label
            })
            
            # Configure grid column
            pieces_frame.columnconfigure(i, weight=1, uniform="card")
        
        # Select Queen by default
        select_piece('Queen')
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_selection,
                              font=("Arial", 11), bg="#6b7280", fg="white", 
                              relief=tk.FLAT, bd=0, width=12, height=2,
                              activebackground="#4b5563")
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        confirm_btn = tk.Button(button_frame, text="Promote", command=confirm_selection,
                               font=("Arial", 11, "bold"), bg="#10b981", fg="white",
                               relief=tk.FLAT, bd=0, width=12, height=2,
                               activebackground="#059669")
        confirm_btn.pack(side=tk.RIGHT)
        
        # Handle window close and keyboard shortcuts
        top.protocol("WM_DELETE_WINDOW", cancel_selection)
        
        # Add keyboard support
        def handle_keypress(event):
            if event.keysym == 'Return' or event.keysym == 'KP_Enter':
                confirm_selection()
            elif event.keysym == 'Escape':
                cancel_selection()
            elif event.keysym in ['1', 'q', 'Q']:
                select_piece('Queen')
            elif event.keysym in ['2', 'r', 'R']:
                select_piece('Rook')
            elif event.keysym in ['3', 'b', 'B']:
                select_piece('Bishop')
            elif event.keysym in ['4', 'n', 'N']:
                select_piece('Knight')
        
        top.bind('<Key>', handle_keypress)
        top.focus_set()  # Ensure dialog has focus for keyboard events
        
        # Wait for selection
        self.root.wait_window(top)
        
        return result

    def handle_click(self, event):
        # Don't allow moves during animation or when reviewing
        if self.animation_in_progress or self.is_reviewing:
            return
            
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
                # Use animation for the move, and check game over after user move
                def after_user_move():
                    self.check_game_over()
                    if not self.board.is_game_over():
                        self.engine_move()
                
                self.animate_move(self.selected_piece, square, move, callback=after_user_move)
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
        # Critical check: Only allow engine to move if it's actually the engine's turn
        if (not self.board.is_game_over() and 
            not self.is_reviewing and 
            self.board.turn == self.engine.color):
            try:
                # Ensure engine has the current board state
                self.engine.board = self.board.copy()
                
                move = self.engine.getBestMove()
                # Validate that we got a proper move object
                if hasattr(move, 'from_square') and hasattr(move, 'to_square'):
                    # Animate engine move
                    self.animate_move(move.from_square, move.to_square, move, 
                                    callback=lambda: self.check_game_over())
                else:
                    # Fallback: pick a random legal move
                    legal_moves = list(self.board.legal_moves)
                    if legal_moves:
                        import random
                        move = random.choice(legal_moves)
                        self.animate_move(move.from_square, move.to_square, move, 
                                        callback=lambda: self.check_game_over())
                    else:
                        self.check_game_over()
            except Exception as e:
                # Handle engine error gracefully - fallback to random legal move
                # Fallback: try random legal move
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    import random
                    move = random.choice(legal_moves)
                    self.animate_move(move.from_square, move.to_square, move, 
                                    callback=lambda: self.check_game_over())
                else:
                    self.check_game_over()
        else:
            # If it's not the engine's turn, don't do anything
            return
            
    def check_game_over(self):
        """Check if the game is over and show dialog if needed"""
        if self.board.is_game_over():
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

    def apply_consistent_backgrounds(self):
        """Ensure all navigation panel components have consistent backgrounds"""
        # This method ensures no white boxes appear when width changes
        def set_bg_recursive(widget, bg_color):
            try:
                if hasattr(widget, 'configure'):
                    widget.configure(bg=bg_color)
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Frame, tk.Label)):
                        set_bg_recursive(child, bg_color)
            except:
                pass
        
        # Apply backgrounds to all sections
        if hasattr(self, 'nav_panel'):
            set_bg_recursive(self.nav_panel, "#ffffff")


if __name__ == "__main__":
    root = tk.Tk()
    board = ch.Board()
    gui = ChessGUI(root, board)
    root.mainloop()
