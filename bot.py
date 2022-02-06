import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from sheets import getVipData

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='vip', help='Return your vip information')
async def vip(ctx, firstName: str, lastName: str):
  data = getVipData(firstName + ' ' + lastName)

  if data:
    embed = discord.Embed(title='Crimson Lotus Vip Status', color=0x7f0505)
    embed.add_field(name='Name', value=data['name'], inline=False)
    embed.add_field(name='Tier', value=data['tier'], inline=False)
    embed.add_field(name='Start Date', value=data['startDate'], inline=False)
    embed.add_field(name='End Date', value=data['endDate'], inline=False)
    embed.add_field(name='Days Remaining ', value=data['remainingDays'], inline=False)

    await ctx.send(embed=embed)
  else:
    await ctx.send(message='No vip data found')

bot.run(TOKEN)
