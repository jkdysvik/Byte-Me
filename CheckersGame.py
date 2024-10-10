import tkinter as tk
from tkinter import messagebox
from camera_tracker import CameraTracker

# Constants for the game
BOARD_SIZE = 8
CELL_SIZE = 75
P1_COLOR = "white"
P2_COLOR = "black"
KING_COLOR = "gold"
MARKER_COLOR = "light green"  # Color for the corner markers
MARKER_SIZE = 12  # Size of the corner markers
PADDING = 10  # Extra padding for the canvas to accommodate markers

class CheckerPiece:
    def __init__(self, player, is_king=False):
        self.player = player
        self.is_king = is_king

    def promote(self):
        self.is_king = True


class CheckersGame:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'P1'
        self.setup_pieces()

    def setup_pieces(self):
        # Setup initial pieces for AI (P2) on the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row > 4:
                        self.board[row][col] = CheckerPiece('P2')

    def update_board_with_physical_pieces(self, piece_positions):
        """
        Update the game board with physical pieces detected by the camera.
        Args:
            piece_positions (list): List of (row, col) tuples for P1 pieces.
        """
        # Remove all P1 pieces from the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.player == 'P1':
                    self.board[row][col] = None
        # Place new P1 pieces based on camera input
        for row, col in piece_positions:
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:  # Ensure the piece is within bounds
                self.board[row][col] = CheckerPiece('P1')

    def ai_move(self):
        # Simple AI: move a random piece for P2 (AI)
        import random

        valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.player == 'P2':
                    # Simple AI move: find an empty adjacent square
                    if row + 1 < BOARD_SIZE and col + 1 < BOARD_SIZE and self.board[row + 1][col + 1] is None:
                        valid_moves.append((row, col, row + 1, col + 1))
                    if row + 1 < BOARD_SIZE and col - 1 >= 0 and self.board[row + 1][col - 1] is None:
                        valid_moves.append((row, col, row + 1, col - 1))

        if valid_moves:
            from_row, from_col, to_row, to_col = random.choice(valid_moves)
            self.board[to_row][to_col] = self.board[from_row][from_col]
            self.board[from_row][from_col] = None
            print(f"AI moved from ({from_row}, {from_col}) to ({to_row}, {to_col})")


class CheckersGUI:
    def __init__(self, root):
        # Increase canvas size to include space for markers
        self.canvas_size = CELL_SIZE * BOARD_SIZE + PADDING * 2
        self.game = CheckersGame()
        self.root = root
        self.root.title("Checkers Game")
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        self.info_panel = tk.Label(self.root, text="Press 'Space' to capture the board state.", height=2)
        self.info_panel.pack()

        # Initialize camera tracker
        self.camera_tracker = CameraTracker()

        # To store the initial setup flag
        self.initial_setup_done = False
        self.current_piece_positions = []

        self.root.bind("<space>", self.update_board)

        self.draw_board()

    def initial_setup(self):
        """Capture the initial board state and set up user's pieces."""
        self.info_panel.config(text="Capturing board setup...")
        self.current_piece_positions = self.camera_tracker.capture_and_process()
        if not self.current_piece_positions:
            self.info_panel.config(text="No pieces detected. Please set up your pieces and press 'Space' again.")
        else:
            self.game.update_board_with_physical_pieces(self.current_piece_positions)
            self.initial_setup_done = True
            self.info_panel.config(text="Game initialized. Press 'Space' to update the board after your move.")
            self.draw_board()

    def update_board(self, event):
        """Capture the board state and update the pieces."""
        self.current_piece_positions = self.camera_tracker.capture_and_process()
        if not self.current_piece_positions:
            self.info_panel.config(text="No pieces detected. Try again.")
            return

        # Update the board with the new P1 positions
        self.game.update_board_with_physical_pieces(self.current_piece_positions)
        self.info_panel.config(text="User move captured. AI is thinking...")

        # AI takes a move
        self.game.ai_move()

        # Redraw the board with updated positions
        self.draw_board()

    def draw_board(self):
        """Draw the checkers board and pieces."""
        self.canvas.delete("all")
        # Offset for centering the board with padding
        board_offset = PADDING
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * CELL_SIZE + board_offset
                y1 = row * CELL_SIZE + board_offset
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.game.board[row][col]
                if piece:
                    self.draw_piece(row, col, piece, board_offset)

            # Draw markers at the intersection between the 4th and 5th cells
            self.draw_markers(board_offset)

    def draw_piece(self, row, col, piece, offset):
        """Draw the pieces on the board."""
        if piece.player == 'P1':
            # Draw user pieces as black circles with white inside
            x1 = col * CELL_SIZE + offset
            y1 = row * CELL_SIZE + offset
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="gray", outline="black", width=3)
        else:
            # Draw AI pieces as black
            x1 = col * CELL_SIZE + offset
            y1 = row * CELL_SIZE + offset
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            color = P2_COLOR if piece.player == 'P2' else P1_COLOR
            if piece.is_king:
                color = KING_COLOR
            self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=color)

    def draw_markers(self, offset):
        """Draw the corner markers for the board."""
        positions = [
            (4 * CELL_SIZE + offset, offset),  # Top center
            (offset, 4 * CELL_SIZE + offset),  # Left center
            (4 * CELL_SIZE + offset, BOARD_SIZE * CELL_SIZE + offset),  # Bottom center
            (BOARD_SIZE * CELL_SIZE + offset, 4 * CELL_SIZE + offset)  # Right center
        ]

        for x, y in positions:
            self.canvas.create_oval(
                x - MARKER_SIZE / 2,
                y - MARKER_SIZE / 2,
                x + MARKER_SIZE / 2,
                y + MARKER_SIZE / 2,
                fill=MARKER_COLOR,
                outline=""
            )

    def on_closing(self):
        """Handle application closing."""
        self.camera_tracker.release()
        self.root.destroy()


# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    checkers_game = CheckersGUI(root)
    root.protocol("WM_DELETE_WINDOW", checkers_game.on_closing)
    root.mainloop()
