# 🇪🇸 Daily Spanish Vocabulary Email Bot

An intelligent email bot that sends you daily Spanish vocabulary (verb + adjective) with **adaptive difficulty** based on your feedback. Learn Spanish one word at a time, delivered to your inbox every morning!

## ✨ Features

- **Daily Vocabulary Emails**: Receive one verb and one adjective every day
- **Adaptive Difficulty**: Reply with "easy", "hard", or "perfect" to adjust difficulty automatically
- **Beautiful Responsive Design**: Emails look great on mobile and desktop
- **No Repetition**: Tracks words already sent - no duplicates until you've seen them all
- **120+ Verbs & Adjectives**: Curated list with conjugations, forms, and example sentences
- **Privacy First**: Runs locally on your machine, no cloud services required
- **Easy Setup**: Interactive wizard guides you through configuration
- **Cross-Platform**: Works on macOS, Linux, and other Unix systems

## 📸 Preview

Each email includes:
- **Verb of the Day**: Spanish word, English translation, conjugations, example sentence
- **Adjective of the Day**: All forms (masculine/feminine, singular/plural), example sentence
- **Current Difficulty Level**: Shows your current learning level
- **Feedback Instructions**: Simple keywords to adjust difficulty

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account with 2FA enabled
- Gmail App Password ([How to create](https://support.google.com/accounts/answer/185833))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TommyWritesCode/daily_spanish_verb.git
   cd daily_spanish_verb
   ```

2. **Run the setup wizard**
   ```bash
   python3 setup.py
   ```

   The wizard will:
   - Guide you through Gmail configuration
   - Install dependencies
   - Create your `.env` file
   - Initialize data files

3. **Test the bot**
   ```bash
   # Preview words without sending
   python3 main.py --dry-run

   # Send a test email
   python3 main.py --test
   ```

4. **Set up daily scheduling**

   **macOS:**
   ```bash
   ./scheduling/launchd_setup.sh
   ```

   **Linux/Unix:**
   ```bash
   crontab -e
   # Add lines from scheduling/crontab_example.txt
   ```

That's it! You'll now receive daily Spanish vocabulary emails.

## 📚 How It Works

### Adaptive Difficulty System

The bot uses a 5-level difficulty system (1.0 = Beginner, 5.0 = Expert):

1. **Initial Level**: Starts at 2.0 (Elementary)
2. **Word Selection**:
   - 70% words at your current level
   - 20% words one level higher (challenge)
   - 10% words one level lower (review)
3. **Feedback Loop**: Reply to any email with:
   - `"easy"` → Increases difficulty by 0.5
   - `"hard"` → Decreases difficulty by 0.5
   - `"perfect"` → Maintains current level

### Example Flow

```
Day 1: Level 2.0 (Elementary) → Words sent
Day 2: You reply "easy" → Level increases to 2.5
Day 3: Level 2.5 → Harder words sent
Day 4: You reply "perfect" → Level stays at 2.5
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file (or use `setup.py`):

```env
# Gmail Configuration
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# Email Settings
RECIPIENT_EMAIL=recipient@gmail.com
SEND_TIME=08:00
```

### Optional Settings

```env
# Custom file paths (defaults shown)
VERBS_FILE=data/verbs.json
ADJECTIVES_FILE=data/adjectives.json
HISTORY_FILE=data/history.json
TEMPLATE_FILE=templates/email_template.html
LOG_FILE=logs/email_bot.log
```

## 📖 Usage

### Manual Commands

```bash
# Send daily email
python3 main.py

# Send test email
python3 main.py --test

# Preview words without sending
python3 main.py --dry-run

# Check for feedback
python3 check_feedback.py

# Verbose logging
python3 main.py --verbose
```

### Scheduling

**macOS (launchd):**
```bash
# Setup (one-time)
./scheduling/launchd_setup.sh

# Check status
launchctl list | grep spanish

# Manual trigger
launchctl start com.spanish.daily

# Unload
launchctl unload ~/Library/LaunchAgents/com.spanish.*.plist
```

**Linux (cron):**
```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths and time)
55 7 * * * cd /path/to/spring_spanish && /path/to/python3 check_feedback.py
0 8 * * * cd /path/to/spring_spanish && /path/to/python3 main.py
```

## 🎯 Difficulty Levels

| Level | Name | Description | Example Verbs |
|-------|------|-------------|---------------|
| 1.0 | Beginner | Basic vocabulary, regular verbs | hablar, comer, vivir |
| 2.0 | Elementary | Common irregular verbs | ser, estar, tener |
| 3.0 | Intermediate | More complex verbs | conocer, parecer, seguir |
| 4.0 | Advanced | Challenging conjugations | conseguir, elegir, convertir |
| 5.0 | Expert | Complex and rare verbs | contradecir, retener, disponer |

## 📁 Project Structure

```
spring_spanish/
├── main.py                      # Main email sending script
├── check_feedback.py            # Feedback checking script
├── setup.py                     # Interactive setup wizard
├── config/
│   └── settings.py              # Configuration loader
├── data/
│   ├── verbs.json              # 120 Spanish verbs
│   ├── adjectives.json         # 120 Spanish adjectives
│   └── history.json            # Usage tracking & preferences
├── templates/
│   └── email_template.html     # Responsive email template
├── utils/
│   ├── word_selector.py        # Adaptive word selection
│   ├── email_sender.py         # Gmail SMTP handler
│   ├── feedback_processor.py  # Feedback parsing
│   └── data_manager.py         # JSON file operations
├── scheduling/
│   ├── launchd_setup.sh        # macOS setup script
│   ├── *.plist.template        # launchd templates
│   └── crontab_example.txt     # Cron examples
└── logs/                        # Log files
```

## 🔧 Customization

### Adding More Words

Edit `data/verbs.json` or `data/adjectives.json`:

```json
{
  "id": 121,
  "spanish": "correr",
  "english": "to run",
  "conjugation": "corro, corres, corre...",
  "example": "Corro cada mañana.",
  "example_en": "I run every morning.",
  "difficulty": 2
}
```

Difficulty scale: 1 (beginner) to 5 (expert)

### Customizing the Email Template

Edit `templates/email_template.html` - it uses inline CSS for maximum email client compatibility.

### Changing Send Time

1. Update `SEND_TIME` in `.env`
2. Re-run the scheduling setup:
   - macOS: `./scheduling/launchd_setup.sh`
   - Linux: Edit your crontab

## 🐛 Troubleshooting

### Email Not Sending

1. **Check credentials**: Make sure `.env` has correct Gmail address and App Password
2. **Verify App Password**: Must be 16 characters (not your regular password)
3. **Check logs**: `tail -f logs/email_bot.log`
4. **Test manually**: `python3 main.py --test`

### Feedback Not Working

1. **Reply to the email**: Don't compose a new email
2. **Use keywords**: Must include "easy", "hard", or "perfect"
3. **Check manually**: `python3 check_feedback.py`
4. **Verify sender**: Reply from the recipient email address

### Scheduling Issues

**macOS:**
```bash
# Check if agents are loaded
launchctl list | grep spanish

# Check logs
tail -f logs/launchd_*.log logs/launchd_*.err
```

**Linux:**
```bash
# Check cron status
service cron status

# View cron logs
grep CRON /var/log/syslog
```

## 📊 Logs

All operations are logged to `logs/email_bot.log`:

```bash
# View recent logs
tail -f logs/email_bot.log

# Search for errors
grep ERROR logs/email_bot.log

# View today's emails
grep "Email sent successfully" logs/email_bot.log
```

## 🔐 Security

- **App Passwords**: Uses Gmail App Passwords (not your main password)
- **Local Only**: All data stays on your machine
- **Secure .env**: File permissions set to 600 (owner only)
- **No Cloud**: No third-party services or APIs

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add more Spanish words to the vocabulary lists
- Improve the email template design
- Fix bugs or add features
- Improve documentation

## 📝 License

MIT License - feel free to use and modify for your own learning!

## 💡 Tips

- **Reply consistently**: The more feedback you give, the better the difficulty adjustment
- **Start beginner**: If unsure, start at a lower difficulty and work up
- **Check history**: View `data/history.json` to see your progress
- **Backup data**: Occasionally backup `data/history.json` to preserve your progress
- **Weekend break**: Edit cron to send only on weekdays: `0 8 * * 1-5`

## 🎓 Learning Tips

1. **Read the email immediately**: Don't let them pile up
2. **Practice the examples**: Read them out loud
3. **Use the words**: Try to use each word in a sentence today
4. **Review regularly**: Old emails are great for review
5. **Adjust difficulty**: Don't hesitate to say "easy" or "hard"

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/TommyWritesCode/daily_spanish_verb/issues)
- **Questions**: Check the troubleshooting section above
- **Feature Requests**: Open an issue with your idea!

---

**¡Buena suerte con tu español!** 🎉

Made with ❤️ for Spanish learners everywhere.
