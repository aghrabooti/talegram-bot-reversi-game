import telebot
import json
import time
from config import TOKEN
from database import db
from game_logic import OthelloGame
from keyboards import invite_keyboard, game_board_keyboard, main_menu_keyboard, game_mode_keyboard
from ai_player import BeginnerAI


bot = telebot.TeleBot(TOKEN)
    
game_messages = {}
ai_games = {}

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    db.register_user(user_id, username, first_name)
    
    text = "Othello Bot\n\nCommands:\n/newgame - Start new game\n/status - Current game"
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['newgame'])
def new_game_command(message):
    text = message.text.strip()
    parts = text.split()
    
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Choose game mode:", reply_markup=game_mode_keyboard())
        return
    
    username_input = parts[1]
    if username_input.startswith('@'):
        username_input = username_input[1:]
    
    from_user = message.from_user.id
    
    active = db.get_user_active_game(from_user)
    if active:
        bot.reply_to(message, "You have active game")
        return
    
    to_user_data = db.get_user_by_username(username_input)
    if not to_user_data:
        bot.reply_to(message, f"User @{username_input} not found")
        return
    
    to_user = to_user_data['user_id']
    
    if from_user == to_user:
        bot.reply_to(message, "Cannot invite yourself")
        return
    
    invite_id = db.create_invite(from_user, to_user)
    
    try:
        bot.send_message(
            to_user,
            f"{message.from_user.first_name} invites to Othello",
            reply_markup=invite_keyboard(invite_id)
        )
        bot.reply_to(message, f"Invite sent to @{username_input}")
    except:
        bot.reply_to(message, "Cannot send invite")

@bot.message_handler(commands=['status'])
def status_command(message):
    user_id = message.from_user.id
    game = db.get_user_active_game(user_id)
    
    if not game:
        bot.reply_to(message, "No active game")
        return
    
    game_logic = OthelloGame(
        json.loads(game['board_state']),
        game['current_player']
    )
    
    moves = game_logic.get_valid_moves(game_logic.current_player)
    
    black_score, white_score = game_logic.get_scores()
    
    text = f"Game #{game['id']}\n\n"
    text += f"⚫ {game['player1_name']}: {black_score}\n"
    text += f"⚪ {game['player2_name']}: {white_score}\n\n"
    text += f"Turn: {game_logic.player_names[game_logic.current_player]}"
    
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=game_board_keyboard(game['id'], moves, game_logic.board)
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        data = call.data
        
        if data == "new_game":
            bot.edit_message_text(
                "Choose game mode:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=game_mode_keyboard()
            )
        
        elif data == "main_menu":
            text = "Othello Bot\n\nCommands:\n/newgame - Start new game\n/status - Current game"
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=main_menu_keyboard()
            )
        
        elif data == "play_friend":
            bot.edit_message_text(
                "To play with a friend:\nUse /newgame @username",
                call.message.chat.id,
                call.message.message_id
            )
        
        elif data == "play_ai":
            start_ai_game(call)
        
        elif data == "scores":
            handle_scores(call)
        
        elif data.startswith("accept:"):
            handle_accept(call)
        
        elif data.startswith("reject:"):
            handle_reject(call)
        
        elif data.startswith("move:"):
            handle_move(call)
        
        elif data.startswith("status:"):
            handle_status(call)
        
        elif data.startswith("resign:"):
            handle_resign(call)
    
    except Exception as e:
        print(f"Error: {e}")
        bot.answer_callback_query(call.id, "Error")

def start_ai_game(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    
    active = db.get_user_active_game(user_id)
    if active:
        bot.answer_callback_query(call.id, "You have active game")
        return
    
    ai_player = BeginnerAI(2)
    
    game_id = db.create_game(
        user_id,
        999999999,
        user_name,
        ai_player.name
    )
    
    game = db.get_game(game_id)
    game_logic = OthelloGame(
        json.loads(game['board_state']),
        game['current_player']
    )
    
    ai_games[game_id] = ai_player
    
    moves = game_logic.get_valid_moves(game_logic.current_player)
    black_score, white_score = game_logic.get_scores()
    
    text = f"Game #{game_id}\n\n"
    text += f"⚫ {user_name}: {black_score}\n"
    text += f"⚪ {ai_player.name}: {white_score}\n\n"
    text += f"Turn: {game_logic.player_names[game_logic.current_player]}"
    
    keyboard = game_board_keyboard(game_id, moves, game_logic.board)
    
    try:
        message = bot.send_message(
            user_id,
            text,
            reply_markup=keyboard
        )
        game_messages[game_id] = {user_id: message.message_id}
    except:
        pass
    
    bot.answer_callback_query(call.id, "AI game started")
    
    if game_logic.current_player == 2:
        time.sleep(1)
        make_ai_move(game_id, game_logic, game)

def handle_scores(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    
    stats_message = stats_manager.format_stats_message(user_id, user_name)
    
    try:
        bot.edit_message_text(
            stats_message,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except:
        bot.send_message(
            call.message.chat.id,
            stats_message
        )
    
    bot.answer_callback_query(call.id, "Statistics loaded")

def handle_accept(call):
    _, invite_id = call.data.split(":")
    invite_id = int(invite_id)
    
    invite = db.get_invite(invite_id)
    if not invite:
        bot.answer_callback_query(call.id, "No invite")
        return
    
    player1_id = invite['from_user']
    player2_id = invite['to_user']
    player1_name = bot.get_chat(player1_id).first_name
    player2_name = bot.get_chat(player2_id).first_name
    
    game_id = db.create_game(
        player1_id, player2_id,
        player1_name,
        player2_name
    )
    
    game = db.get_game(game_id)
    game_logic = OthelloGame(
        json.loads(game['board_state']),
        game['current_player']
    )
    
    moves = game_logic.get_valid_moves(game_logic.current_player)
    black_score, white_score = game_logic.get_scores()
    
    text = f"Game #{game_id}\n\n"
    text += f"⚫ {player1_name}: {black_score}\n"
    text += f"⚪ {player2_name}: {white_score}\n\n"
    text += f"Turn: {game_logic.player_names[game_logic.current_player]}"
    
    keyboard = game_board_keyboard(game_id, moves, game_logic.board)
    
    bot.edit_message_text(
        "Game started",
        call.message.chat.id,
        call.message.message_id
    )
    
    game_messages[game_id] = {}
    
    for player_id in [player1_id, player2_id]:
        try:
            message = bot.send_message(
                player_id,
                text,
                reply_markup=keyboard
            )
            game_messages[game_id][player_id] = message.message_id
        except:
            pass
    
    bot.answer_callback_query(call.id, "Started")

def handle_reject(call):
    _, invite_id = call.data.split(":")
    invite_id = int(invite_id)
    
    invite = db.get_invite(invite_id)
    if not invite:
        bot.answer_callback_query(call.id, "No invite")
        return
    
    db.update_invite(invite_id, "rejected")
    
    bot.edit_message_text(
        "Rejected",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.answer_callback_query(call.id)

def handle_move(call):
    _, game_id, row, col = call.data.split(":")
    game_id = int(game_id)
    row = int(row)
    col = int(col)
    
    game = db.get_game(game_id)
    if not game:
        bot.answer_callback_query(call.id, "No game")
        return
    
    game_logic = OthelloGame(
        json.loads(game['board_state']),
        game['current_player']
    )
    
    current_player = game['player1'] if game_logic.current_player == 1 else game['player2']
    if call.from_user.id != current_player:
        bot.answer_callback_query(call.id, "Not your turn")
        return
    
    if not game_logic.make_move(row, col, game_logic.current_player):
        bot.answer_callback_query(call.id, "Invalid move")
        return
    
    db.update_game_board(game_id, game_logic.board, game_logic.current_player)
    
    moves = game_logic.get_valid_moves(game_logic.current_player)
    black_score, white_score = game_logic.get_scores()
    
    text = f"Game #{game_id}\n\n"
    text += f"⚫ {game['player1_name']}: {black_score}\n"
    text += f"⚪ {game['player2_name']}: {white_score}\n\n"
    text += f"Turn: {game_logic.player_names[game_logic.current_player]}"
    
    keyboard = game_board_keyboard(game_id, moves, game_logic.board)
    
    if game_id in game_messages:
        for player_id, message_id in game_messages[game_id].items():
            try:
                bot.edit_message_text(
                    text,
                    chat_id=player_id,
                    message_id=message_id,
                    reply_markup=keyboard
                )
            except:
                pass
    
    if game_logic.is_game_over():
        winner = game_logic.get_winner()
        if winner == 0:
            result = "Draw"
            db.end_game(game_id, "draw")
        else:
            winner_name = game['player1_name'] if winner == 1 else game['player2_name']
            result = f"Winner: {winner_name}"
            if winner == 1:
                db.end_game(game_id, "player1")
            else:
                db.end_game(game_id, "player2")
        
        final_text = f"Game Over\n\n"
        final_text += f"⚫ {game['player1_name']}: {black_score}\n"
        final_text += f"⚪ {game['player2_name']}: {white_score}\n\n"
        final_text += result
        
        if game_id in game_messages:
            for player_id, message_id in game_messages[game_id].items():
                try:
                    bot.edit_message_text(
                        final_text,
                        chat_id=player_id,
                        message_id=message_id
                    )
                except:
                    pass
        
        if game_id in ai_games:
            del ai_games[game_id]
        
        bot.answer_callback_query(call.id, "Game over")
    else:
        bot.answer_callback_query(call.id, "Move made")
        
        if game_id in ai_games:
            time.sleep(1)
            make_ai_move(game_id, game_logic, game)

def make_ai_move(game_id, game_logic, game):
    if game_id not in ai_games:
        return
    
    ai_player = ai_games[game_id]
    
    if game_logic.current_player != ai_player.player_color:
        return
    
    ai_move = ai_player.make_move(game_logic)
    
    if not ai_move:
        return
    
    row, col = ai_move
    
    game_logic.make_move(row, col, ai_player.player_color)
    
    db.update_game_board(game_id, game_logic.board, game_logic.current_player)
    
    moves = game_logic.get_valid_moves(game_logic.current_player)
    black_score, white_score = game_logic.get_scores()
    
    text = f"Game #{game_id}\n\n"
    text += f"⚫ {game['player1_name']}: {black_score}\n"
    text += f"⚪ {ai_player.name}: {white_score}\n\n"
    text += f"Turn: {game_logic.player_names[game_logic.current_player]}"
    
    keyboard = game_board_keyboard(game_id, moves, game_logic.board)
    
    if game_id in game_messages:
        for player_id, message_id in game_messages[game_id].items():
            try:
                bot.edit_message_text(
                    text,
                    chat_id=player_id,
                    message_id=message_id,
                    reply_markup=keyboard
                )
            except:
                pass
    
    if game_logic.is_game_over():
        winner = game_logic.get_winner()
        if winner == 0:
            result = "Draw"
            db.end_game(game_id, "draw")
        else:
            winner_name = game['player1_name'] if winner == 1 else ai_player.name
            result = f"Winner: {winner_name}"
            if winner == 1:
                db.end_game(game_id, "player1")
            else:
                db.end_game(game_id, "player2")
        
        final_text = f"Game Over\n\n"
        final_text += f"⚫ {game['player1_name']}: {black_score}\n"
        final_text += f"⚪ {ai_player.name}: {white_score}\n\n"
        final_text += result
        
        if game_id in game_messages:
            for player_id, message_id in game_messages[game_id].items():
                try:
                    bot.edit_message_text(
                        final_text,
                        chat_id=player_id,
                        message_id=message_id
                    )
                except:
                    pass
        
        if game_id in ai_games:
            del ai_games[game_id]
    else:
        if game_id in ai_games and game_logic.current_player == ai_player.player_color:
            time.sleep(1)
            make_ai_move(game_id, game_logic, game)

def handle_status(call):
    _, game_id = call.data.split(":")
    game_id = int(game_id)
    
    game = db.get_game(game_id)
    if not game:
        bot.answer_callback_query(call.id, "No game")
        return
    
    game_logic = OthelloGame(
        json.loads(game['board_state']),
        game['current_player']
    )
    
    moves = game_logic.get_valid_moves(game_logic.current_player)
    black_score, white_score = game_logic.get_scores()
    
    text = f"Game #{game_id}\n\n"
    text += f"⚫ {game['player1_name']}: {black_score}\n"
    text += f"⚪ {game['player2_name']}: {white_score}\n\n"
    text += f"Turn: {game_logic.player_names[game_logic.current_player]}"
    
    keyboard = game_board_keyboard(game_id, moves, game_logic.board)
    
    if game_id in game_messages and call.from_user.id in game_messages[game_id]:
        try:
            bot.edit_message_text(
                text,
                chat_id=call.from_user.id,
                message_id=game_messages[game_id][call.from_user.id],
                reply_markup=keyboard
            )
        except:
            pass
    
    bot.answer_callback_query(call.id, "Updated")

def handle_resign(call):
    _, game_id = call.data.split(":")
    game_id = int(game_id)
    
    game = db.get_game(game_id)
    if not game:
        bot.answer_callback_query(call.id, "No game")
        return
    
    user_id = call.from_user.id
    
    if user_id == game['player1']:
        winner = "player2"
        winner_name = game['player2_name']
        loser_name = game['player1_name']
    else:
        winner = "player1"
        winner_name = game['player1_name']
        loser_name = game['player2_name']
    
    db.end_game(game_id, winner)
    
    text = f"Game #{game_id}\n\n"
    text += f"{loser_name} resigned\n"
    text += f"🏆 Winner: {winner_name}"
    
    if game_id in game_messages:
        for player_id, message_id in game_messages[game_id].items():
            try:
                bot.edit_message_text(
                    text,
                    chat_id=player_id,
                    message_id=message_id
                )
            except:
                pass
    
    if game_id in ai_games:
        del ai_games[game_id]
    
    bot.answer_callback_query(call.id, "Resigned")

if __name__ == "__main__":
    print("Bot started")
    bot.infinity_polling()
