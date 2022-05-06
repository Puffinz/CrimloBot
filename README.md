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
| BOT_PREFIX          | Prefix used for all commands. Defaults to '!'                                            |
| BOT_MANAGER_ROLE_ID | Id for the discord role that will be able to use manager commands                        |
| VIP_ROLE_ID         | Id for the discord role that is a VIP                                                    |
| SERVER_ID           | Id for your discord server that the bot is on                                            |
| CRON_CHANNEL_ID     | Channel where vip cron logs will output                                                  |
| CRON_SCHEDULE       | Schedule that the cron for VIPs will be run on                                           |
| API_HOST            | URL of the api used to interact with the vip storage                                     |
| API_KEY             | Authorization key for the api                                                            |

3. Run the bot
```
python bot.py
```

6. Use `!help` (use the prefix you defined if not using the default) in a channel with the bot to see the list of commands. You must have the role that coresponds to BOT_MANAGER_ROLE_ID.
