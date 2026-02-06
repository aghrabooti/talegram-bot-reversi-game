import sqlite3

class StatsManager:
    def __init__(self, db_path="games.db"):
        self.db_path = db_path
    
    def get_player_stats(self, user_id):
        """Get player statistics with minimal database queries"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        stats = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'total_games': 0,
            'opponents': {}
        }
        
        cur.execute("""
            SELECT player2, player2_name, winner FROM games 
            WHERE player1=? AND status='ended'
        """, (user_id,))
        
        for game in cur.fetchall():
            opponent_id, opponent_name, winner = game
            stats['total_games'] += 1
            
            opponent_key = f"{opponent_id}_{opponent_name}"
            if opponent_key not in stats['opponents']:
                stats['opponents'][opponent_key] = {
                    'id': opponent_id,
                    'name': opponent_name,
                    'wins': 0,
                    'losses': 0,
                    'draws': 0
                }
            
            if winner == "player1":
                stats['wins'] += 1
                stats['opponents'][opponent_key]['wins'] += 1
            elif winner == "player2":
                stats['losses'] += 1
                stats['opponents'][opponent_key]['losses'] += 1
            elif winner == "draw":
                stats['draws'] += 1
                stats['opponents'][opponent_key]['draws'] += 1
        
        cur.execute("""
            SELECT player1, player1_name, winner FROM games 
            WHERE player2=? AND status='ended'
        """, (user_id,))
        
        for game in cur.fetchall():
            opponent_id, opponent_name, winner = game
            stats['total_games'] += 1
            
            opponent_key = f"{opponent_id}_{opponent_name}"
            if opponent_key not in stats['opponents']:
                stats['opponents'][opponent_key] = {
                    'id': opponent_id,
                    'name': opponent_name,
                    'wins': 0,
                    'losses': 0,
                    'draws': 0
                }
            
            if winner == "player2":
                stats['wins'] += 1
                stats['opponents'][opponent_key]['wins'] += 1
            elif winner == "player1":
                stats['losses'] += 1
                stats['opponents'][opponent_key]['losses'] += 1
            elif winner == "draw":
                stats['draws'] += 1
                stats['opponents'][opponent_key]['draws'] += 1
        
        conn.close()
        return stats
    
    def format_stats_message(self, user_id, user_name):
        """Format stats into a readable message"""
        stats = self.get_player_stats(user_id)
        
        if stats['total_games'] == 0:
            return f"📊 {user_name}'s Statistics\n\nNo games played yet!"
        
        message = f"📊 {user_name}'s Statistics\n\n"
        message += f"🏆 Wins: {stats['wins']}\n"
        message += f"💔 Losses: {stats['losses']}\n"
        message += f"🤝 Draws: {stats['draws']}\n"
        message += f"🎮 Total Games: {stats['total_games']}\n"
        
        win_rate = (stats['wins'] / stats['total_games']) * 100 if stats['total_games'] > 0 else 0
        message += f"📈 Win Rate: {win_rate:.1f}%\n\n"
        
        if stats['opponents']:
            message += "👥 Opponents:\n"
            for opp_key, opp_data in stats['opponents'].items():
                total_games = opp_data['wins'] + opp_data['losses'] + opp_data['draws']
                message += f"• {opp_data['name']}: {opp_data['wins']}W/{opp_data['losses']}L/{opp_data['draws']}D ({total_games} games)\n"
        
        return message

stats_manager = StatsManager()
