# Telegram Bot Setup Guide

## Overview
The Nextbase Auto Telegram Bot allows users to report traffic incidents via Telegram by sending photos and answering questions.

## Prerequisites
- Python 3.7+
- Telegram account
- OpenAI API key
- Telegram Bot Token (from BotFather)

## Setup Instructions

### 1. Create Your Telegram Bot

1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "Nextbase Auto Helper")
   - Choose a username (must end in 'bot', e.g., "nextbase_auto_bot")
4. BotFather will give you a **Bot Token** - save this!

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=your_openai_api_key_for_cli_tool_only
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python telegram_bot.py
```

You should see: `Bot is running... Press Ctrl+C to stop.`

### 5. Test Your Bot

1. Open Telegram and search for your bot username
2. Send `/start` to begin
3. Upload a dashcam photo
4. Answer the questions
5. Receive the formatted report summary

## Bot Commands

- `/start` - Start a new incident report
- `/help` - Show help information
- `/cancel` - Cancel current report

## Usage Flow

1. **Send /start** - Bot greets you
2. **Upload photo** - Photo of the incident
3. **Answer questions** - Incident type, registration, color, date, time, location, personal details
4. **Review summary** - All collected information split into easy-to-copy messages
5. **Copy and paste** - Use the formatted data to fill the Nextbase form

## Questions Asked by Bot

### Incident Details
- Street name where incident occurred

### Personal Information
- First name
- Last name
- Email address
- Phone number
- Home address (line 1 & 2)
- County
- Postcode
- Occupation
- Date of birth (DD/MM/YYYY)
- Place of birth
- Gender

## Auto-Extracted from Photo (CLI Tool Only)

The CLI tool uses OpenAI Vision to extract:
- Date
- Time
- Day of week
- Vehicle registration
- Vehicle color
- Incident type (corner/pavement parking)

**Note:** The Telegram bot asks users for all details manually (no AI required).

## Running as a Service (Linux)

Create a systemd service file at `/etc/systemd/system/nextbase-bot.service`:

```ini
[Unit]
Description=Nextbase Auto Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/nextbase-auto
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable nextbase-bot
sudo systemctl start nextbase-bot
sudo systemctl status nextbase-bot
```

## Privacy & Security

- Conversations are stored temporarily in memory only
- No personal data is saved permanently by the bot
- Photo files are stored temporarily in `/tmp` and cleaned up
- Users must manually submit reports to police
- All data collection follows GDPR principles

## Troubleshooting

**Bot not responding:**
- Check bot token is correct in `.env`
- Verify bot is running: `ps aux | grep telegram_bot`
- Check logs for errors

**Image analysis fails:**
- Only applicable to CLI tool (uses OpenAI)
- Telegram bot asks for all details manually

**Bot token error:**
- Get new token from @BotFather: `/token`
- Update `.env` file with new token

## Support

For issues or questions, open an issue on GitHub:
https://github.com/JimShady/nextbase-auto
