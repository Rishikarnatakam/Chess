# Chess Game with Minimax AI

A Python chess game with a graphical interface and a minimax-based AI opponent.  
This project is designed for anyone who wants to play chess against a computer, study basic AI, or learn about GUI programming in Python.

---

## Features

- **Play chess against the computer**: Choose to play as White or Black.
- **Minimax AI**: The computer opponent uses the minimax algorithm with alpha-beta pruning.
- **Adjustable difficulty**: Select the AI search depth (2, 3, or 4).
- **All chess rules supported**: Includes pawn promotion, castling, en passant, and all draw conditions (stalemate, threefold/fivefold repetition, fifty-move rule, insufficient material).
- **User-friendly GUI**: Built with Tkinter, featuring piece images, move highlighting, and dialogs for game events.
- **No external dependencies except `chess` and `Pillow`**.

---

## Installation & Usage

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```sh
   python main.py
   ```

---

## Project Structure

```
chess_3/
├── main.py              # Entry point
├── chess_gui.py         # GUI logic (Tkinter)
├── ChessEngine.py       # Minimax AI engine
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── images/              # Chess piece images (12 PNGs)
│   ├── wk.png
│   ├── wq.png
│   └── ...etc.
```

---

## How it Works

- When you start the game, you choose your color and the AI difficulty.
- The board is displayed with images for each piece.
- Click to select and move your pieces; legal moves are highlighted.
- The AI responds using minimax search with standard chess piece values (Pawn=1, Knight=3, Bishop=3.1, Rook=5, Queen=9).
- The game ends with a win, loss, or draw, and a dialog explains the result.

---

## Notes

- The `images/` folder must be present in the same directory as the code files for the game to display pieces correctly.
- The project uses only open-source Python packages.

---



*Enjoy playing and studying chess with your own Python AI!*