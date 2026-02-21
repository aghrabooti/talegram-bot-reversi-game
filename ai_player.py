import random

class BeginnerAI:
    def __init__(self, player_color):
        self.player_color = player_color
        self.name = "🤖 AI"
    
    def make_move(self, game_logic):
        valid_moves = game_logic.get_valid_moves(self.player_color)
        
        if not valid_moves:
            return None
        
        return random.choice(valid_moves)
