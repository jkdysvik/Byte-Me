import tkinter as tk
from tkinter import messagebox

# Constants for the game
BOARD_SIZE = 8
CELL_SIZE = 60
P1_COLOR = "white"
P2_COLOR = "black"
HIGHLIGHT_COLOR = "yellow"
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
                    if row < 3:
                        self.board[row][col] = CheckerPiece('P1')
                    elif row > 4:
                        self.board[row][col] = CheckerPiece('P2')

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

        return moves + jumps

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
                        valid_pieces.append((row, col, moves))

        if valid_pieces:
            from_row, from_col, moves = random.choice(valid_pieces)
            to_move = random.choice(moves)
            if len(to_move) == 4:  # It's a jump move
                to_row, to_col, mid_row, mid_col = to_move
            else:
                to_row, to_col = to_move
            self.move_piece(from_row, from_col, to_row, to_col)
            return from_row, from_col, to_row, to_col
        return None


class CheckersGUI:
    def __init__(self, root):
        # Increase canvas size to include space for markers
        self.canvas_size = CELL_SIZE * BOARD_SIZE + PADDING * 2
        self.game = CheckersGame()
        self.root = root
        self.root.title("Checkers Game")
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        self.info_panel = tk.Label(self.root, text="", height=2)
        self.info_panel.pack()

        self.canvas.bind("<ButtonPress-1>", self.click_handler)
        self.canvas.bind("<B1-Motion>", self.drag_handler)
        self.canvas.bind("<ButtonRelease-1>", self.release_handler)

        self.drag_data = {"piece": None, "start_row": None, "start_col": None, "piece_id": None}
        self.draw_board()

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
        if piece.player == 'P1':  # Skip drawing P2 pieces
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
        # Calculate positions for markers at the intersection between the 4th and 5th cells on the edges
        positions = [
            (4 * CELL_SIZE +  MARKER_SIZE, offset),  # Top edge, between the 4th and 5th cells
            (offset, 4 * CELL_SIZE + offset),  # Left edge, between the 4th and 5th cells
            (4.01 * CELL_SIZE +  MARKER_SIZE, BOARD_SIZE * CELL_SIZE + offset +1),  # Bottom edge, between the 4th and 5th cells
            (BOARD_SIZE * CELL_SIZE + offset, 4.02 * CELL_SIZE + offset)   # Right edge, between the 4th and 5th cells
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

    def click_handler(self, event):
        board_offset = PADDING
        row, col = (event.y - board_offset) // CELL_SIZE, (event.x - board_offset) // CELL_SIZE
        piece = self.game.board[row][col] if self.game.is_within_bounds(row, col) else None
        if piece and piece.player == self.game.current_player:
            self.drag_data["piece"] = piece
            self.drag_data["start_row"] = row
            self.drag_data["start_col"] = col
            self.drag_data["piece_id"] = self.canvas.create_oval(event.x - CELL_SIZE // 2, event.y - CELL_SIZE // 2,
                                                                 event.x + CELL_SIZE // 2, event.y + CELL_SIZE // 2,
                                                                 fill=P1_COLOR if piece.player == 'P1' else P2_COLOR)

    def drag_handler(self, event):
        if self.drag_data["piece"]:
            self.canvas.coords(self.drag_data["piece_id"],
                               event.x - CELL_SIZE // 2, event.y - CELL_SIZE // 2,
                               event.x + CELL_SIZE // 2, event.y + CELL_SIZE // 2)

    def release_handler(self, event):
        board_offset = PADDING
        row, col = (event.y - board_offset) // CELL_SIZE, (event.x - board_offset) // CELL_SIZE
        if self.drag_data["piece"] and self.game.is_within_bounds(row, col):
            start_row, start_col = self.drag_data["start_row"], self.drag_data["start_col"]

            valid_moves = self.game.get_valid_moves(start_row, start_col)
            for move in valid_moves:
                if len(move) == 4:  # Capture move
                    to_row, to_col, _, _ = move
                else:
                    to_row, to_col = move
                if (row, col) == (to_row, to_col):
                    self.game.move_piece(start_row, start_col, to_row, to_col)
                    self.game.switch_player()
                    self.info_panel.config(text=f"Player {self.game.current_player} moved ({start_row}, {start_col}) to ({row}, {col})")
                    self.root.after(500, self.ai_turn)
                    break

            self.canvas.delete(self.drag_data["piece_id"])
            self.drag_data = {"piece": None, "start_row": None, "start_col": None, "piece_id": None}
            self.draw_board()

    def ai_turn(self):
        if self.game.current_player == 'P2':
            move = self.game.ai_move()
            if move:
                from_row, from_col, to_row, to_col = move
                self.info_panel.config(text=f"AI moved ({from_row}, {from_col}) to ({to_row}, {to_col})")
            self.game.switch_player()
            self.draw_board()


# Run the game
root = tk.Tk()
checkers_game = CheckersGUI(root)
root.mainloop()
