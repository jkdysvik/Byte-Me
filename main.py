import cv2
import numpy as np
import random

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

    def find_player_pieces(self):
        # Load the image
        image = cv2.imread("IMG_2248.jpg")
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Adjust the HSV range for green detection (more restrictive)
        lower_green = np.array([40, 50, 50])  # Increased the minimum saturation and value
        upper_green = np.array([80, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        # Adjust the HSV range for red detection (red spans around the hue 0/180 boundary)
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # Perform morphological operations to close gaps in both masks
        kernel = np.ones((5, 5), np.uint8)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

        # Function to find and filter dots based on color and contour area
        def find_dots(mask, lower_hue, upper_hue, min_contour_area=100):
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            dots_coordinates = []

            for contour in contours:
                if cv2.contourArea(contour) > min_contour_area:
                    # Calculate the average color of the contour in the original image
                    mask_temp = np.zeros(mask.shape, np.uint8)
                    cv2.drawContours(mask_temp, [contour], -1, 255, -1)
                    mean_val = cv2.mean(image, mask=mask_temp)

                    # Convert mean color to HSV
                    mean_hsv = cv2.cvtColor(np.uint8([[mean_val[:3]]]), cv2.COLOR_BGR2HSV)[0][0]

                    # Ensure the average color is within the correct range
                    if lower_hue <= mean_hsv[0] <= upper_hue:
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            center_x = int(M["m10"] / M["m00"])
                            center_y = int(M["m01"] / M["m00"])
                            dots_coordinates.append((center_x, center_y))

            return dots_coordinates

        # Find green and red dots
        green_dots_coordinates = find_dots(mask_green, lower_green[0], upper_green[0])
        red_dots_coordinates = find_dots(mask_red, lower_red1[0], upper_red2[0])

        def merge_close_points(points, threshold=50):
            merged_points = []
            while points:
                point = points.pop(0)
                close_points = [p for p in points if np.linalg.norm(np.array(point) - np.array(p)) < threshold]
                points = [p for p in points if p not in close_points]
                all_points = [point] + close_points
                avg_x = int(np.mean([p[0] for p in all_points]))
                avg_y = int(np.mean([p[1] for p in all_points]))
                merged_points.append((avg_x, avg_y))
            return merged_points

        # Merge close points for both green and red dots
        green_dots_coordinates = merge_close_points(green_dots_coordinates)
        red_dots_coordinates = merge_close_points(red_dots_coordinates)

        # Print the coordinates of the detected green and red dots
        print("Green Dots:", green_dots_coordinates)
        print(f"Number of detected green dots: {len(green_dots_coordinates)}")
        print("Red Dots:", red_dots_coordinates)
        print(f"Number of detected red dots: {len(red_dots_coordinates)}")

        # Optional: draw the detected points on the image for visualization
        for coord in green_dots_coordinates:
            cv2.circle(image, coord, 10, (0, 255, 0), -1)  # Draw green dots on the detected points
        for coord in red_dots_coordinates:
            cv2.circle(image, coord, 10, (0, 0, 255), -1)  # Draw red dots on the detected points

        min = 1000000000
        max = 0
        for coordinate in green_dots_coordinates:
            if coordinate[1] < min:
                min = coordinate[1]
            elif coordinate[1] > max:
                max = coordinate[1]

            if coordinate[0] < min:
                min = coordinate[0]
            elif coordinate[0] > max:
                max = coordinate[0]

        print(min)
        print(max)
        edges = []
        for i in range(0, 9):
            edges.append(i * (max - min) / 8)

        for dot in red_dots_coordinates:
            x, y = dot
            # Find the row index by comparing y with vertical edges
            row = next(k for k, edge in enumerate(edges) if y < edge)
            # Find the column index by comparing x with horizontal edges
            col = next(j for j, edge in enumerate(edges) if x < edge)
            game.add_piece(Piece(col-1, 8 - row, 1))

    def play_game(self):
        turn = 0
        while True:
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
game.find_player_pieces()
game.create_opponent_pieces()
game.play_game()
