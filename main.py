import cv2
import numpy as np
import random
from find_dots import find_dots
from AI import AI

class Piece:
    def __init__(self, x, y, piece_type):
        self.x = x
        self.y = y
        self.type = piece_type  # 1 for player piece, 2 for opponent piece
        self.king = False

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def place_piece(self, piece):
        self.board[8 - piece.y][piece.x - 1] = piece.type

    def find_piece(self, x, y):
        """Find the piece object located at (x, y)"""
        for row in self.board:
            for piece in row:
                if piece and piece.x == x and piece.y == y:
                    return piece
        return None

    def remove_piece(self, piece):
        self.board[8 - piece.y][piece.x - 1] = None

    def move_piece(self, piece, new_x, new_y):
        self.remove_piece(piece)
        piece.move(new_x, new_y)
        self.place_piece(piece)

    def print_board(self):
        print("   1   2   3   4   5   6   7   8")
        print("  +---+---+---+---+---+---+---+---+")
        for i, row in enumerate(self.board):
            row_str = f"{8 - i} | " + " | ".join(
                ["1" if cell == 1 else "2" if cell == 2 else " " for cell in row]) + f" | {8 - i}"
            print(row_str)
            print("  +---+---+---+---+---+---+---+---+")
        print("   1   2   3   4   5   6   7   8")

    def check_square(self, x, y):
        return self.board[8 - y][x - 1] if 0 <= x - 1 < 8 and 0 <= 8 - y < 8 else None

    def get_board_array(self):
        """Convert the internal board representation into an array of 'w' and 'b'"""
        board_array = []
        for row in self.board:
            board_row = ["w" if cell == 1 else "b" if cell == 2 else " " for cell in row]
            board_array.append(board_row)
        print(board_array)
        result = AI(board_array)
        return result



class Game:
    def __init__(self):
        self.board = Board()
        self.player_pieces = []
        self.opponent_pieces = []
        self.player_legal_moves = []
        self.opponent_legal_moves = []
        self.previous_board = []
        self.new_board = []

    def add_piece(self, piece):
        self.board.place_piece(piece)
        if piece.type == 1:
            self.player_pieces.append(piece)
        elif piece.type == 2:
            self.opponent_pieces.append(piece)

    def create_opponent_pieces(self):
        for f in range (0,9):
            if f % 2 == 0:
                game.add_piece(Piece(f, 7, 2))
            else:
                game.add_piece(Piece(f, 6, 2))
                game.add_piece(Piece(f, 8, 2))



    def find_legal_moves(self, pieces, legal_moves):
        for piece in pieces:
            x, y = piece.x, piece.y
            self.check_and_add_move(piece, x - 1, y - 1, legal_moves)
            self.check_and_add_move(piece, x - 1, y + 1, legal_moves)
            self.check_and_add_move(piece, x + 1, y - 1, legal_moves)
            self.check_and_add_move(piece, x + 1, y + 1, legal_moves)

    def check_and_add_move(self, piece, x, y, legal_moves):
        if 1 <= x <= 8 and 1 <= y <= 8 and self.board.check_square(x, y) is None:
            legal_moves.append((piece, x, y))

    def find_player_pieces(self, imgnr):
        points = find_dots(imgnr)
        for point in points:
            game.add_piece(Piece(point[0], point[1], 1))

    def check_legality(self, new_board, player_legal_moves):
        return None

    def find_difference(self, previous_board, new_board):
        removed_piece = None
        moved_piece = None

        # Detect the removed piece
        for prev_piece in previous_board:
            if prev_piece not in new_board:
                removed_piece = prev_piece
                break

        # Detect the moved piece
        for new_piece in new_board:
            if new_piece not in previous_board:
                moved_piece = new_piece
                break

        if removed_piece and moved_piece:
            print(f"Piece moved from {removed_piece} to {moved_piece}")
            return removed_piece, moved_piece
        else:
            print("No move detected.")
            return None, None

    def play_game(self):
        turn = 0
        game.find_player_pieces("2245")
        self.previous_board = find_dots("2245")  # Initial board state
        self.board.print_board()

        while True:

            if turn != 0:
                self.board.print_board()
            # Clear previous moves
            self.player_legal_moves.clear()
            self.opponent_legal_moves.clear()

            # Find legal moves for both players
            self.find_legal_moves(self.player_pieces, self.player_legal_moves)
            self.find_legal_moves(self.opponent_pieces, self.opponent_legal_moves)

            # Remove duplicates
            self.player_legal_moves = list(dict.fromkeys(self.player_legal_moves))
            self.opponent_legal_moves = list(dict.fromkeys(self.opponent_legal_moves))

            if not self.player_legal_moves and not self.opponent_legal_moves:
                print("No more legal moves available. Game over!")
                break

            if turn % 2 == 0:  # Player's turn
                imgnr = input("Img: ")

                # Save the current board state as the new board
                self.new_board = find_dots(imgnr)

                # Find the difference between the previous and new board
                removed_piece, moved_piece = self.find_difference(self.previous_board, self.new_board)

                if removed_piece and moved_piece:
                    # Execute the move on the board
                    chosen_piece = Piece(removed_piece[0], removed_piece[1], 1)  # Assuming it's a player piece
                    new_x, new_y = moved_piece[0], moved_piece[1]
                    self.board.move_piece(chosen_piece, new_x, new_y)

                    # Update the previous board to the new one
                    self.previous_board = self.new_board.copy()
                else:
                    print("No valid move detected.")

            else:  # Opponent's turn
                if self.opponent_legal_moves:
                    best_move = AI(self.board.get_board_array())
                    print("Ai move: " + best_move)
                    old_x, old_y = best_move[0]
                    new_x, new_y = best_move[1]

                    # Find the piece at (old_x, old_y)
                    chosen_piece = self.board.find_piece(old_x, old_y)

                    if chosen_piece:
                        print(f"Opponent moves piece at ({old_x},{old_y}) to ({new_x},{new_y})")
                        self.board.move_piece(chosen_piece, new_x, new_y)
                        print(self.board.get_board_array())
                    else:
                        print(f"No piece found at ({old_x},{old_y})")
                else:
                    print("No legal moves available for the opponent.")

            # Increment the turn counter
            turn += 1


game = Game()

game.create_opponent_pieces()
game.play_game()
