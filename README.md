# CHESS

A chess game implementing the **Minimax algorithm with Alpha-Beta pruning** for intelligent AI gameplay. Built with Python and Tkinter GUI.

## Overview

This project demonstrates a complete chess engine using the **Minimax algorithm** - a decision-making algorithm widely used in game theory and AI. The engine evaluates thousands of possible moves to find the optimal play at each turn.

## Core Features

- **Minimax AI Engine**: Recursive tree search with Alpha-Beta pruning optimization
- **Configurable Engine Depth**: User-selectable depth (2-7) for optimal performance on any computer  
- **Complete Chess Implementation**: All official rules including special moves and endgame conditions
- **Interactive GUI**: Visual board with smooth animations and move history navigation
- **Game Analysis**: Review previous positions and export games in PGN format

## Algorithm Implementation

The AI engine (`ChessEngine.py`) uses:

**Minimax with Alpha-Beta Pruning:**
- Recursively searches the game tree to a specified depth
- Evaluates leaf positions using material and positional factors
- Alpha-beta pruning eliminates up to 75% of unnecessary branches
- Returns the best move for the current position

**Position Evaluation:**
- Material values: Pawn(1), Knight(3), Bishop(3.1), Rook(5), Queen(9)
- Opening development bonuses for early game play
- Mate threat detection for tactical awareness
- Random factor to avoid repetitive play

**Engine Depth Performance Guide:**
- Start with **Depth 3** for most computers
- If moves take too long, reduce depth
- If you want stronger play and have a powerful computer, increase depth
- Depth 5+ may cause significant delays on older/slower computers

## Quick Start

```bash
# Clone and run
git clone https://github.com/yourusername/chess.git
cd chess
pip install -r requirements.txt
python main.py
```

## Technical Requirements

- **Python**: 3.7 or higher
- **Dependencies**: `chess` (game logic), `Pillow` (image processing)

## Project Structure

```
chess/
├── main.py              # Application entry point
├── ChessEngine.py       # Minimax algorithm core implementation
├── chess_gui.py         # Tkinter GUI and game interface
├── requirements.txt     # Python package dependencies
└── images/              # Chess piece graphics (12 PNG files)
```

## How to Play

1. Run `python main.py` to start
2. Choose your color (White/Black) and engine depth (2-7)
3. Click pieces to move them on the board
4. Use navigation buttons to review move history
5. Game automatically detects checkmate, stalemate, and draws

**Note**: If the engine takes too long to move, restart and choose a lower depth setting.

## Educational Value

This implementation is ideal for:
- Learning the **Minimax algorithm** in practice
- Understanding **Alpha-Beta pruning** optimization
- Studying **game tree search** techniques
- Chess programming and AI development
- Teaching recursive algorithms and game theory

## License

**MIT License** - Free to use, modify, and distribute for any purpose.

```
Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.