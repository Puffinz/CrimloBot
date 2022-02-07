import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from sheets import getVipData, addVipData

load_dotenv()

bot = commands.Bot(command_prefix=os.getenv('BOT_PREFIX'))

async def sendVipInfo(ctx, name, data):
  if data:
    embed = discord.Embed(title='Crimson Lotus Vip Status', color=0x7f0505)
    embed.add_field(name='Name', value=data['name'], inline=False)
    embed.add_field(name='Start Date', value=data['startDate'], inline=False)
    embed.add_field(name='End Date', value=data['endDate'], inline=False)
    embed.add_field(name='Days Remaining ', value=data['remainingDays'], inline=False)

    await ctx.send(embed=embed)
  else:
    await ctx.send('No vip data found for: ' + name)

@bot.command(name='vip', help='Return vip information for your user')
async def vip(ctx):
  name = ctx.message.author.nick or ctx.message.author.name
  data = getVipData(name)

  await sendVipInfo(ctx, name, data)

@bot.command(name='getVip', help='Return vip information of the specified user')
@commands.has_role(os.getenv('BOT_MANAGER_ROLE'))
async def getVip(ctx, taggedUser: discord.User):
  name = taggedUser.display_name
  data = getVipData(name)

  await sendVipInfo(ctx, name, data)

@bot.command(name='addVip', help='Grant vip to the specified user')
@commands.has_role(os.getenv('BOT_MANAGER_ROLE'))
async def addVip(ctx, taggedUser: discord.User):
  name = taggedUser.display_name
  addVipData(name)

  data = getVipData(name)
  await sendVipInfo(ctx, name, data)

bot.run(os.getenv('BOT_TOKEN'))
