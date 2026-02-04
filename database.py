import sqlite3
import json

class Database:
    def __init__(self, db_path="games.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER,
            to_user INTEGER,
            status TEXT DEFAULT 'pending'
        )
        """)
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1 INTEGER,
            player2 INTEGER,
            player1_name TEXT,
            player2_name TEXT,
            board_state TEXT DEFAULT '[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,1,2,0,0,0],[0,0,0,2,1,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]',
            current_player INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active'
        )
        """)
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            player_id INTEGER,
            move TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.cur.execute("PRAGMA table_info(games)")
        columns = [col[1] for col in self.cur.fetchall()]
        if 'winner' not in columns:
            self.cur.execute("ALTER TABLE games ADD COLUMN winner TEXT")
        
        self.conn.commit()
            
    def register_user(self, user_id, username, first_name):
        self.cur.execute(
            """INSERT OR REPLACE INTO users (user_id, username, first_name) 
            VALUES (?, ?, ?)""",
            (user_id, username, first_name)
        )
        self.conn.commit()
    
    def get_user_by_username(self, username):
        self.cur.execute("SELECT * FROM users WHERE username=?", (username.lower(),))
        row = self.cur.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2]
            }
        return None
    
    def create_invite(self, from_user, to_user):
        self.cur.execute(
            "INSERT INTO invites (from_user, to_user, status) VALUES (?, ?, 'pending')",
            (from_user, to_user)
        )
        self.conn.commit()
        return self.cur.lastrowid
    
    def get_invite(self, invite_id):
        self.cur.execute("SELECT * FROM invites WHERE id=?", (invite_id,))
        row = self.cur.fetchone()
        if row:
            return {
                'id': row[0],
                'from_user': row[1],
                'to_user': row[2],
                'status': row[3]
            }
        return None
    
    def update_invite(self, invite_id, status):
        self.cur.execute("UPDATE invites SET status=? WHERE id=?", (status, invite_id))
        self.conn.commit()
    
    def create_game(self, player1, player2, player1_name, player2_name):
        self.cur.execute(
            """INSERT INTO games (player1, player2, player1_name, player2_name) 
            VALUES (?, ?, ?, ?)""",
            (player1, player2, player1_name, player2_name)
        )
        self.conn.commit()
        return self.cur.lastrowid
    
    def get_game(self, game_id):
        self.cur.execute("SELECT * FROM games WHERE id=?", (game_id,))
        row = self.cur.fetchone()
        if row:
            return {
                'id': row[0],
                'player1': row[1],
                'player2': row[2],
                'player1_name': row[3],
                'player2_name': row[4],
                'board_state': row[5],
                'current_player': row[6],
                'status': row[7]
            }
        return None
    
    def update_game_board(self, game_id, board_state, current_player):
        self.cur.execute(
            "UPDATE games SET board_state=?, current_player=? WHERE id=?",
            (json.dumps(board_state), current_player, game_id)
        )
        self.conn.commit()
    
    def end_game(self, game_id, winner):
        winner_text = None
        if winner == 1:
            winner_text = "player1"
        elif winner == 2:
            winner_text = "player2"
        elif winner == 0:
            winner_text = "draw"
        
        self.cur.execute(
            "UPDATE games SET status='ended', winner=? WHERE id=?",
            (winner_text, game_id)
        )
        self.conn.commit()
    
    def add_move(self, game_id, player_id, move):
        self.cur.execute(
            "INSERT INTO moves (game_id, player_id, move) VALUES (?, ?, ?)",
            (game_id, player_id, move)
        )
        self.conn.commit()
    
    def get_user_active_game(self, user_id):
        self.cur.execute(
            "SELECT * FROM games WHERE (player1=? OR player2=?) AND status='active'",
            (user_id, user_id)
        )
        row = self.cur.fetchone()
        if row:
            return {
                'id': row[0],
                'player1': row[1],
                'player2': row[2],
                'player1_name': row[3],
                'player2_name': row[4],
                'board_state': row[5],
                'current_player': row[6],
                'status': row[7]
            }
        return None

db = Database()