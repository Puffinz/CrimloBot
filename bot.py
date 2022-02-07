import os
import discord

from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from sheets import getVipData, addVipMonth

load_dotenv()

BOT_PREFIX = os.getenv('BOT_PREFIX')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_MANAGER_ROLE_ID = int(os.getenv('BOT_MANAGER_ROLE_ID'))
VIP_ROLE_ID = int(os.getenv('VIP_ROLE_ID'))

bot = commands.Bot(command_prefix=BOT_PREFIX)

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

# !help
bot.remove_command('help') # Remove the default help command
@bot.command(name='help')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def help(ctx):
  embed = discord.Embed(title = 'Help')

  embed.add_field(name='!vip', value='Return vip information for your user', inline=False)
  embed.add_field(name='!getVip <user>', value='Return vip information of the specified user', inline=False)
  embed.add_field(name='!addVip <user>', value='Grant 1 month of vip to the specified user', inline=False)

  await ctx.send(embed=embed)

# !vip
@bot.command(name='vip')
async def vip(ctx):
  name = ctx.message.author.nick or ctx.message.author.name
  data = getVipData(name)

  await sendVipInfo(ctx, name, data)

# !getVip
@bot.command(name='getVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def getVip(ctx, taggedUser: discord.User):
  name = taggedUser.display_name
  data = getVipData(name)

  await sendVipInfo(ctx, name, data)

# !addVip
@bot.command(name='addVip', help='Grant vip to the specified user')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def addVip(ctx, taggedUser: discord.Member):
  name = taggedUser.display_name

  addVipMonth(name)

  # Add VIP role
  role = get(ctx.message.author.guild.roles, id=VIP_ROLE_ID)
  await taggedUser.add_roles(role)
  data = getVipData(name)

  await sendVipInfo(ctx, name, data)

bot.run(BOT_TOKEN)
