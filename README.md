# Othello Telegram Bot

A Telegram bot for playing the classic board game Othello (Reversi) with friends. This bot allows two players to play Othello in real-time with an interactive board interface.

## Features

- 🎮 **Two-player Othello game** - Play against friends in real-time
- 🎯 **Interactive board** - Click-based interface with inline keyboards
- ⚫ **Real-time updates** - Both players see the updated board instantly
- 📱 **Telegram integration** - Works in private chats and groups
- 💾 **Game state persistence** - Games are saved in SQLite database
- 🏆 **Win detection** - Automatic winner determination
- 🔄 **Game status tracking** - Check current game status anytime
- 🤖 **Beginner AI opponent** - Play against a simple AI if you don’t have a friend online

## How to Play

### Basic Commands:
- `/start` - Start the bot and see main menu
- `/newgame` - Choose the game type (against human or AI)
- `/status` - Check your current game status
- `/help` - Show game rules and instructions

### Game Rules:
1. Black (⚫) always moves first
2. Place your piece to flank opponent's pieces
3. Flanked pieces are flipped to your color
4. Game ends when no moves are possible
5. Player with most pieces wins

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Local Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd othello-bot
```

2. **Create virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create environment file:**
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
```

5. **Run the bot:**
```bash
python bot.py
```

### Project Structure
```
othello-bot/
├── bot.py              # Main bot application
├── database.py         # Database operations
├── game_logic.py       # Othello game logic
├── keyboards.py        # Telegram inline keyboards
├── config.py          # Configuration loader
├── requirements.txt    # Python dependencies
├── .env              # Environment variables (not in repo)
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## Deployment

### GitHub Actions (Free)
1. Add your bot token as a secret in GitHub:
   - Go to Repository Settings → Secrets and variables → Actions
   - Add new secret: `BOT_TOKEN` with your token value

2. Push code to trigger deployment:
```bash
git add .
git commit -m "Deploy bot"
git push origin main
```

### Other Free Hosting Options:
- **PythonAnywhere**: Free tier with scheduled tasks
- **Railway.app**: Free credits monthly
- **Replit**: Free hosting with auto-reload
- **Heroku**: Free tier (with some limitations)

## Database Schema

The bot uses SQLite with the following tables:
- `users`: Registered Telegram users
- `invites`: Game invitations
- `games`: Active and completed games
- `moves`: Game move history

## Game Logic

The Othello implementation includes:
- 8x8 game board
- Valid move detection
- Piece flipping logic
- Turn management
- Win condition checking
- Score tracking

## Development

### Adding Features
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

### Testing
Run the bot locally and test with:
- Game invitations
- Move validation
- Win detection
- Multiple simultaneous games

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure code follows existing style
5. Submit a pull request

## Known Issues
- GitHub Actions has 6-hour job limit (bot restarts automatically)
- Some Telegram clients may have keyboard rendering issues
- Database may need manual cleanup for abandoned games

## License

This project is open source and available under the MIT License.

## Support

For issues and feature requests:
1. Check existing issues
2. Create new issue with details
3. Include error logs and steps to reproduce

## Acknowledgments

- Telegram Bot API for the platform
- Python developers for excellent libraries
- Othello/Reversi game community

---

*This README was written with assistance from AI to ensure clarity and completeness.*
