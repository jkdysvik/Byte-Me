import cv2
import numpy as np
import random
from find_dots import find_dots

class Piece:
    def __init__(self, x, y, piece_type):
        self.x = x
        self.y = y
        self.type = piece_type  # 1 for player piece, 2 for opponent piece

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def place_piece(self, piece):
        self.board[8 - piece.y][piece.x - 1] = piece.type

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

class Game:
    def __init__(self):
        self.board = Board()
        self.player_pieces = []
        self.opponent_pieces = []
        self.player_legal_moves = []
        self.opponent_legal_moves = []

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



    def play_game(self):
        turn = 0
        while True:
            imgnr = input("Img: ")
            game.find_player_pieces(imgnr)
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
                if self.player_legal_moves:
                    print("Player legal moves:")
                    for i, move in enumerate(self.player_legal_moves):
                        piece, x, y = move
                        print(f"{i}: Move piece at ({piece.x},{piece.y}) to ({x},{y})")

                    # Player chooses a move
                    move_index = int(input("Choose move by index: "))
                    chosen_piece, new_x, new_y = self.player_legal_moves[move_index]

                    # Execute the move
                    self.board.move_piece(chosen_piece, new_x, new_y)
                else:
                    print("No legal moves available for the player.")
            else:  # Opponent's turn
                if self.opponent_legal_moves:
                    opp_move_index = random.randint(0, len(self.opponent_legal_moves) - 1)
                    chosen_piece, new_x, new_y = self.opponent_legal_moves[opp_move_index]
                    print(f"Opponent moves piece at ({chosen_piece.x},{chosen_piece.y}) to ({new_x},{new_y})")

                    # Execute the move
                    self.board.move_piece(chosen_piece, new_x, new_y)
                else:
                    print("No legal moves available for the opponent.")

            # Increment the turn counter
            turn += 1


game = Game()

game.create_opponent_pieces()
game.play_game()
