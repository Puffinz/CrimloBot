# CrimloBot
Discord bot for The Crimson Lotus

## How to use the bot:
1. Install dependencies
```
pip install -r requirements.txt
```
2. Set up the required environment variables

| Variable            | Description                                                                              |
| ------------------- | ---------------------------------------------------------------------------------------- |
| BOT_TOKEN           | Token for the bot application from discord                                               |
| BOT_PREFIX          | Prefix used for all commands (eg. '!')                                                   |
| VIP_SHEET_ID        | ID for the Google Sheets spreadsheet that the VIP information is on (find it in the url) |
| BOT_MANAGER_ROLE_ID | Id for the discord role that will be able to use manager commands                        |
| VIP_ROLE_ID         | Id for the discord role that is a VIP                                                    |

3. Add the service account key file named as 'creds.json' to the project. It must have access to the Google Sheets API.

4. Share a google sheet with the proper format to the service account

5. Run the bot
```
python bot.py
```

6. Use !help in a channel with the bot to see the list of commands. You must have the role that coresponds to BOT_MANAGER_ROLE_ID.
