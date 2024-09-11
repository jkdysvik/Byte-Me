from random import randrange
import time
import random

N = 8

AI_path = []  # record the best path found by AI


# set up the board
def initBoard():
    board = [[' ' for j in range(N)] for i in range(N)]

    # the init board, one can change it for easy debug
    B = [".b.b.b.b",
         "b.b.b.b.",
         ".b.b.b.b",
         "........",
         "........",
         "w.w.w.w.",
         ".w.w.w.w",
         "w.w.w.w."]

    for y in range(N):
        for x in range(N):
            if (y + x) % 2 != 1:
                continue
            if B[y][x] in ['b', 'B', 'w', 'W']:
                board[y][x] = B[y][x]
    return board


# check whether the move list is valid
def canMove(board, move_list, color):
    paths = getAllMoves(board, color)
    for path in paths:
        if len(path) == len(move_list): # the move is in the valid move list ?
            same = True
            for i in range(len(move_list)):
                if path[i] != move_list[i]:
                    same = False
                    break
            if same:
                return True
    return False

# make the move on the board
def makeMove(board, move_list):
    regicide = False
    for i in range(1, len(move_list)):
        (y1, x1) = move_list[i - 1]
        (y2, x2) = move_list[i]

        board[y1][x1], board[y2][x2] = ' ', board[y1][x1]
        if abs(y2 - y1) == 2:  # is jump ?
            my, mx = (y1 + y2) >> 1, (x1 + x2) >> 1
            if board[my][mx] in ['B', 'W']:  # eat a King
                regicide = True
            board[my][mx] = ' '
        # update to the King ?
        toKing(board, y2, x2, regicide)


def upper(color):
    if color in ['b', 'B']:
        return 'B'
    if color in ['w', 'W']:
        return 'W'


def op(color):
    if color in ['b', 'B']:
        return 'w'
    if color in ['w', 'w']:
        return 'b'


# AI function
def gameOver(board):
    b, w = 0, 0
    for y in range(N):
        for x in range(N):
            if board[y][x] in ['b', 'B']:
                b += 1
            if board[y][x] in ['w', 'W']:
                w += 1
    if b == 0:
        print("White win!")
        return 'w'  # w win
    if w == 0:
        print("Black win!")
        return 'b'  # b win
    return None


def evaluation(board, color):
    score = 0
    for y in range(N):
        for x in range(N):
            if board[y][x] == 'B': score += 10
            if board[y][x] == 'b': score += 1
            if board[y][x] == 'W': score -= 10
            if board[y][x] == 'w': score -= 1
    if color == 'b':
        return score
    else:
        return -score


# the checker become the King ?
def toKing(board, y, x, regicide):
    if board[y][x] == 'b' and (y == N - 1 or regicide):
        board[y][x] = 'B'
    if board[y][x] == 'w' and (y == 0 or regicide):
        board[y][x] = 'W'


# get all the valid moves: first jump. if no jump, then move
def getAllMoves(board, color='b'):
    # use dfs to get all the jumps
    def dfs(board, path, y, x, paths):
        color = board[y][x]
        dir = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        jump_num = 0
        for k in range(len(dir)):  # try 4 directions from (y,x)
            if color == 'b' and dir[k][0] < 0: continue  # 'b' can only move down
            if color == 'w' and dir[k][0] > 0: continue  # 'w' can only move up

            my, mx = y + dir[k][0], x + dir[k][1]
            ey, ex = y + 2 * dir[k][0], x + 2 * dir[k][1]
            if 0 <= ey and ey < N and 0 <= ex and ex < N:
                color2 = board[my][mx]
                regicide = False  # eat the King ?
                if color in ['b', 'w'] and color2 in ['B', 'W']:
                    regicide = True
                # jump from (y,x), by (my,mx), to (ey,ex)
                if color2 in [op(color), upper(op(color))] and board[ey][ex] == ' ':
                    jump_num += 1
                    board[y][x], board[my][mx], board[ey][ex] = ' ', ' ', board[y][x]
                    path.append((y, x))

                    if regicide:
                        P = [xy for xy in path]
                        P.append((ey, ex))
                        paths.append(P)
                    else:
                        dfs(board, path, ey, ex, paths)

                    # recover
                    board[y][x], board[my][mx], board[ey][ex] = board[ey][ex], color2, ' '
                    del path[-1]

        # if jump_num == 0 and len(path)>=1:
        if len(path) >= 1:
            P = [xy for xy in path]
            P.append((y, x))
            paths.append(P)

    def getJumpPaths(board, color='b'):
        paths = []

        # for 'b', search from bottom to up
        # for 'w', search from up to bottom
        sy, ty, dy = N - 1, -1, -1
        if color == 'w':
            sy, ty, dy = 0, N, 1
        y = sy
        while y != ty:
            for x in range(N):
                if board[y][x] in [color, upper(color)]:
                    path = []
                    dfs(board, path, y, x, paths)
            y += dy
        return paths

    def getMovePaths(board, color='b'):
        paths = []
        dir = [[-1, -1], [-1, 1], [1, -1], [1, 1]]

        # for 'b', search from bottom to up
        # for 'w', search from up to bottom
        sy, ty, dy = N - 1, -1, -1
        if color == 'w':
            sy, ty, dy = 0, N, 1
        y = sy
        while y != ty:
            for x in range(N):
                if board[y][x] in [color, upper(color)]:
                    for k in range(len(dir)):
                        if color == 'b' and dir[k][0] < 0: continue  # 'b' can only move down
                        if color == 'w' and dir[k][0] > 0: continue  # 'w' can only move up
                        ey, ex = y + dir[k][0], x + dir[k][1]
                        if 0 <= ey and ey < N and 0 <= ex and ex < N and board[ey][ex] == ' ':
                            paths.append([(y, x), (ey, ex)])

            y += dy
        return paths

    # first get all the Jump
    paths = getJumpPaths(board, color)
    if paths:
        return paths

    # if no Jump, get the Move
    return getMovePaths(board, color)


# minimax function, to get the best move and score
def minimax(board, depth, max_depth, color, alpha, beta):
    global AI_path
    # game over
    win = gameOver(board)
    if win in ['b', 'w']:
        if (win == color and depth % 2 == 0) or (win != color and depth % 2 != 0):
            return 99999
        else:
            return -99999

    # meet the max search depth
    if depth >= max_depth:
        score = evaluation(board, color)
        if depth % 2 == 0:
            return score
        else:
            return -score

    # go through each possible move
    paths = getAllMoves(board, color)
    maxScore, minScore = -99999, 99999
    for path in paths:
        board2 = [[board[y][x] for x in range(N)] for y in range(N)]
        makeMove(board2, path)

        score = minimax(board2, depth + 1, max_depth, op(color), alpha, beta)
        if depth % 2 == 0:
            if maxScore < score:
                maxScore = score
                if depth == 0: AI_path = path
            alpha = max(alpha, score)
        else:
            minScore = min(minScore, score)
            beta = min(beta, score)

        if alpha >= beta:  # alpha-beta prun
            break

    if depth % 2 == 0:
        return maxScore
    else:
        return minScore


def callMinimax(board, color, search_depth):
    global AI_path
    
    alpha, beta = -999999, 999999
    AI_path = []
    minimax(board, 0, search_depth, color, alpha, beta)
    if color == 'b' and AI_path == []:
        print("White win!")
        return AI_path
    elif color == 'w' and AI_path == []:
        print("Black win!")
        return AI_path
    else:
        print('AI: ', AI_path)
    
    return AI_path


def AI():
    board = [[' ', 'b', ' ', 'b', ' ', 'b', ' ', 'b', ],
             ['b', ' ', 'b', ' ', 'b', ' ', 'b', ' ', ],
             [' ', '', ' ', 'b', ' ', 'b', ' ', 'b', ],
             ['b', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ],
             [' ', 'w', ' ', ' ', ' ', ' ', ' ', ' ', ],
             ['w', ' ', ' ', ' ', ' ', 'w', 'w', ' ', ],
             [' ', 'w', ' ', 'w', ' ', 'w', ' ', 'w', ],
             [' ', ' ', 'w', ' ', 'w', ' ', 'w', ' ', ]]
    path = callMinimax(board, 'b', 2)
    makeMove(board, path)
    # print(board)
    b = [''.join(line) for line in board]
    b = '\n'.join(b)
    print(b)


AI()
