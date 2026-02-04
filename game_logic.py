import json

class OthelloGame:
    def __init__(self, board_state=None, current_player=1):
        self.board = board_state or self.get_initial_board()
        self.current_player = current_player
        self.player_symbols = {1: '⚫', 2: '⚪'}
        self.player_names = {1: 'Black', 2: 'White'}
    
    def get_initial_board(self):
        board = [[0 for _ in range(8)] for _ in range(8)]
        board[3][3] = 1
        board[3][4] = 2
        board[4][3] = 2
        board[4][4] = 1
        return board
    
    def is_valid_move(self, row, col, player):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        
        if self.board[row][col] != 0:
            return False
        
        opponent = 3 - player
        directions = [(-1,-1), (-1,0), (-1,1),
                     (0,-1),         (0,1),
                     (1,-1),  (1,0),  (1,1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if not (0 <= r < 8 and 0 <= c < 8):
                continue
            
            if self.board[r][c] != opponent:
                continue
            
            r += dr
            c += dc
            
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == 0:
                    break
                if self.board[r][c] == player:
                    return True
                r += dr
                c += dc
        
        return False
    
    def get_valid_moves(self, player):
        moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col, player):
                    moves.append((row, col))
        return moves
    
    def make_move(self, row, col, player):
        if not self.is_valid_move(row, col, player):
            return False
        
        self.board[row][col] = player
        opponent = 3 - player
        
        directions = [(-1,-1), (-1,0), (-1,1),
                     (0,-1),         (0,1),
                     (1,-1),  (1,0),  (1,1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if not (0 <= r < 8 and 0 <= c < 8):
                continue
            
            if self.board[r][c] != opponent:
                continue
            
            to_flip = []
            to_flip.append((r, c))
            r += dr
            c += dc
            
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == 0:
                    break
                if self.board[r][c] == player:
                    for fr, fc in to_flip:
                        self.board[fr][fc] = player
                    break
                to_flip.append((r, c))
                r += dr
                c += dc
        
        self.current_player = 3 - player
        
        if not self.get_valid_moves(self.current_player):
            self.current_player = 3 - self.current_player
        
        return True
    
    def get_scores(self):
        black = sum(row.count(1) for row in self.board)
        white = sum(row.count(2) for row in self.board)
        return black, white
    
    def is_game_over(self):
        black_moves = self.get_valid_moves(1)
        white_moves = self.get_valid_moves(2)
        return not black_moves and not white_moves
    
    def get_winner(self):
        black, white = self.get_scores()
        if black > white:
            return 1
        elif white > black:
            return 2
        else:
            return 0