import tkinter as tk
from tkinter import messagebox
from camera_tracker import CameraTracker

# Constants for the game
BOARD_SIZE = 8
CELL_SIZE = 75
P1_COLOR = "white"
P2_COLOR = "black"
KING_COLOR = "gold"
MARKER_COLOR = "green"  # Color for the corner markers
MARKER_SIZE = 10  # Size of the corner markers
PADDING = 10  # Extra padding for the canvas to accommodate markers

# Directions for movement
DIRECTIONS = {
    'P1': [(1, -1), (1, 1)],  # Down-left, down-right
    'P2': [(-1, -1), (-1, 1)]  # Up-left, up-right
}


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
        # Setup initial pieces on the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row > 4:
                        self.board[row][col] = CheckerPiece('P2')
        # P1 pieces will be set up based on camera input

    def is_within_bounds(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece is None:
            return []

        moves = []
        jumps = []
        directions = DIRECTIONS[piece.player]
        if piece.is_king:
            directions += [(-d[0], -d[1]) for d in directions]  # Allow movement in all directions for king

        for dr, dc in directions:
            # Simple move
            new_row, new_col = row + dr, col + dc
            if self.is_within_bounds(new_row, new_col) and self.board[new_row][new_col] is None:
                moves.append((new_row, new_col))
            # Jump move
            jump_row, jump_col = row + 2 * dr, col + 2 * dc
            if self.is_within_bounds(jump_row, jump_col):
                mid_row, mid_col = row + dr, col + dc
                mid_piece = self.board[mid_row][mid_col]
                if mid_piece and mid_piece.player != piece.player and self.board[jump_row][jump_col] is None:
                    jumps.append((jump_row, jump_col, mid_row, mid_col))

        return jumps if jumps else moves  # Prioritize jumps

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Check if it's a jump and remove the captured piece
        if abs(from_row - to_row) == 2:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            self.board[mid_row][mid_col] = None

        # Promote to king if reaching the opposite side
        if (piece.player == 'P1' and to_row == BOARD_SIZE - 1) or (piece.player == 'P2' and to_row == 0):
            piece.promote()

    def switch_player(self):
        self.current_player = 'P2' if self.current_player == 'P1' else 'P1'

    def ai_move(self):
        # Simple AI: Randomly pick a move from available pieces
        import random

        valid_pieces = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.player == self.current_player:
                    moves = self.get_valid_moves(row, col)
                    if moves:
                        for move in moves:
                            if len(move) == 4:  # It's a jump move
                                valid_pieces.insert(0, (row, col, move))  # Prioritize jumps
                            else:
                                valid_pieces.append((row, col, move))

        if valid_pieces:
            from_row, from_col, move = valid_pieces[0]
            if len(move) == 4:  # Jump move
                to_row, to_col, mid_row, mid_col = move
                self.board[mid_row][mid_col] = None  # Remove captured piece
                # Inform user to remove their piece
                self.captured_piece = (mid_row, mid_col)
            else:
                to_row, to_col = move
                self.captured_piece = None

            self.move_piece(from_row, from_col, to_row, to_col)
            return from_row, from_col, to_row, to_col
        return None

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
            if self.is_within_bounds(row, col):
                self.board[row][col] = CheckerPiece('P1')


class CheckersGUI:
    def __init__(self, root):
        # Increase canvas size to include space for markers
        self.canvas_size = CELL_SIZE * BOARD_SIZE + PADDING * 2
        self.game = CheckersGame()
        self.root = root
        self.root.title("Checkers Game")
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        self.info_panel = tk.Label(self.root, text="Initializing game...", height=2)
        self.info_panel.pack()

        # Initialize camera tracker
        self.camera_tracker = CameraTracker()
        # Capture initial board state
        self.initial_setup()

        self.previous_piece_positions = self.current_piece_positions.copy()

        self.root.bind("<space>", self.confirm_move)

        self.draw_board()

    def initial_setup(self):
        """Capture the initial board state and set up user's pieces."""
        self.info_panel.config(text="Capturing initial board setup...")
        self.current_piece_positions = self.camera_tracker.capture_and_process()
        if not self.current_piece_positions:
            self.info_panel.config(text="No pieces detected. Please set up your pieces and press 'Space'.")
            self.root.bind("<space>", self.initial_setup)
        else:
            self.game.update_board_with_physical_pieces(self.current_piece_positions)
            self.info_panel.config(text="Game initialized. Press 'Space' after making your move.")
            self.root.bind("<space>", self.confirm_move)

    def draw_board(self):
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
        if piece.player == 'P1':  # Skip drawing P1 pieces (physical)
            return
        x1 = col * CELL_SIZE + offset
        y1 = row * CELL_SIZE + offset
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        color = P2_COLOR if piece.player == 'P2' else P1_COLOR
        if piece.is_king:
            color = KING_COLOR
        self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=color)

    def draw_markers(self, offset):
        # Calculate positions for markers at the center of each side
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

    def confirm_move(self, event):
        self.current_piece_positions = self.camera_tracker.capture_and_process()
        if not self.current_piece_positions:
            self.info_panel.config(text="No pieces detected. Try again.")
            return

        # Update the game board with the new positions
        self.game.update_board_with_physical_pieces(self.current_piece_positions)

        # Detect move
        if self.game.current_player != 'P1':
            self.info_panel.config(text="Not your turn.")
            return

        previous_set = set(self.previous_piece_positions)
        current_set = set(self.current_piece_positions)

        if previous_set != current_set:
            # A move has occurred
            moved_pieces = previous_set.symmetric_difference(current_set)
            if len(moved_pieces) == 2:
                from_pos = list(previous_set - current_set)[0]
                to_pos = list(current_set - previous_set)[0]
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                # Validate the move
                valid_moves = self.game.get_valid_moves(from_row, from_col)
                if (to_row, to_col) in [(m[0], m[1]) if len(m) == 2 else (m[0], m[1]) for m in valid_moves]:
                    # Move is valid
                    self.game.move_piece(from_row, from_col, to_row, to_col)
                    self.game.switch_player()
                    self.info_panel.config(text="Valid move. AI is thinking...")
                    self.draw_board()
                    self.root.after(500, self.ai_turn)
                else:
                    # Invalid move
                    self.info_panel.config(text="Invalid move. Try again.")
                    # Revert to previous state
                    self.game.update_board_with_physical_pieces(self.previous_piece_positions)
                    self.draw_board()
            else:
                # Multiple pieces moved or pieces added/removed
                self.info_panel.config(text="Invalid move. Ensure only one piece is moved.")
                # Revert to previous state
                self.game.update_board_with_physical_pieces(self.previous_piece_positions)
                self.draw_board()
        else:
            self.info_panel.config(text="No move detected.")

        self.previous_piece_positions = self.current_piece_positions.copy()

    def ai_turn(self):
        if self.game.current_player == 'P2':
            move = self.game.ai_move()
            if move:
                from_row, from_col, to_row, to_col = move
                self.info_panel.config(text=f"AI moved ({from_row}, {from_col}) to ({to_row}, {to_col})")
                if self.game.captured_piece:
                    cap_row, cap_col = self.game.captured_piece
                    self.info_panel.config(text=f"AI captured your piece at ({cap_row}, {cap_col}). Please remove it.")
            else:
                self.info_panel.config(text="AI has no valid moves. You win!")
            self.game.switch_player()
            self.draw_board()
        else:
            self.info_panel.config(text="Your turn. Make your move and press 'Space'.")

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
