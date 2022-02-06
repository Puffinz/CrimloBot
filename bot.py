import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='vip', help='Responds with a random quote from Brooklyn 99')
async def vip(ctx):
  embed = discord.Embed(title='Crimson Lotus Vip Status', color=0x7f0505)
  embed.add_field(name='Name', value='Eros Primal', inline=False)
  embed.add_field(name='Tier', value='Plus', inline=False)
  embed.add_field(name='Start Date', value='10/28', inline=False)
  embed.add_field(name='End Date', value='2/12', inline=False)
  embed.add_field(name='Days Remaining ', value='7', inline=False)

  await ctx.send(embed=embed)

bot.run(TOKEN)
