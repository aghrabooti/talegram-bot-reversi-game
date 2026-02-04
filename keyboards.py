from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def invite_keyboard(invite_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Accept", callback_data=f"accept:{invite_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject:{invite_id}")
    )
    return keyboard

def game_board_keyboard(game_id, valid_moves, board_state=None):
    keyboard = InlineKeyboardMarkup(row_width=8)
    
    symbols = {0: '⬜', 1: '⚫', 2: '⚪'}
    
    for row in range(8):
        button_row = []
        for col in range(8):
            if board_state:
                cell = board_state[row][col]
                if cell == 0 and (row, col) in valid_moves:
                    button_text = "🔘"
                else:
                    button_text = symbols.get(cell, '⬜')
            else:
                button_text = '⬜'
                if (row, col) in valid_moves:
                    button_text = "🔘"
            
            button_row.append(
                InlineKeyboardButton(button_text, callback_data=f"move:{game_id}:{row}:{col}")
            )
        keyboard.add(*button_row)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Status", callback_data=f"status:{game_id}"),
        InlineKeyboardButton("🏳️ Resign", callback_data=f"resign:{game_id}")
    )
    
    return keyboard

def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🎮 New Game", callback_data="new_game"),
        InlineKeyboardButton("📊 Scores", callback_data="scores")
    )
    return keyboard