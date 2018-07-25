Ninja bot can forward specific commands to predefined groups. It is used for reporting abuses and spam by non-priviledged users.

## Group pairing 
Bot can be deployed to multiple groups. It scans for several commands like /admin, /spam, /scam, /kick and /ban. Bot forwards these commands acording to this dictionary https://github.com/wirfeon/ninja/blob/master/bot.py#L20-L22

## Settings
Bot needs 2 enviromental properties:
* WEB_HOOK - URL address on which the bot is listening HTTP requests
* BOT_TOKEN - Bot token created by Telegram. Keep this token in private.

## Starting up
```python3 bot.py```
# News bot
