import os
import discord
import aiocron

from datetime import date
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from sheets import getVipData, addVipMonth, updateVipName, removeExpiredVips

load_dotenv()

BOT_PREFIX = os.getenv('BOT_PREFIX') or '!'
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_MANAGER_ROLE_ID = int(os.getenv('BOT_MANAGER_ROLE_ID'))
VIP_ROLE_ID = int(os.getenv('VIP_ROLE_ID'))
SERVER_ID = int(os.getenv('SERVER_ID'))
CRON_CHANNEL_ID = int(os.getenv('CRON_CHANNEL_ID'))
CRON_SCHEDULE = os.getenv('CRON_SCHEDULE')

CRIMLO_COLOR = int(0xe00000)

intents = discord.Intents.default()
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

async def sendVipInfo(ctx, name, data):
  if data:
    embed = discord.Embed(title='Crimson Lotus VIP Status', color=CRIMLO_COLOR)
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
  embed = discord.Embed(title = 'Help', color=CRIMLO_COLOR)

  embed.add_field(name=BOT_PREFIX + 'vip', value='Return vip information for your user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'getVip @<user>', value='Return vip information of the specified user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'addVip @<user>', value='Grant 1 month of vip to the specified user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'cleanVips', value='Remove expired vips from the main sheet, and add them to the history table. Also removes vip role from the users.', inline=False)
  embed.add_field(name=BOT_PREFIX + 'renameVip @<user>', value='Update the name of an existing vip - use this if a vip has changed their discord name', inline=False)

  await ctx.send(embed=embed)

# !vip
@bot.command(name='vip')
async def vip(ctx):
  name = ctx.message.author.display_name
  id = ctx.message.author.id

  data = getVipData(id)

  await sendVipInfo(ctx, name, data)

# !getVip
@bot.command(name='getVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def getVip(ctx, taggedUser: discord.User):
  data = getVipData(taggedUser.id)

  await sendVipInfo(ctx, taggedUser.display_name, data)

# !addVip
@bot.command(name='addVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def addVip(ctx, taggedUser: discord.Member):
  name = taggedUser.display_name
  id = taggedUser.id

  addVipMonth(name, id)

  # Add VIP role
  role = get(ctx.message.author.guild.roles, id=VIP_ROLE_ID)
  await taggedUser.add_roles(role)

  data = getVipData(id)

  await sendVipInfo(ctx, name, data)

# !renameVip
@bot.command(name='renameVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def addVip(ctx, taggedUser: discord.Member):
  id = taggedUser.id
  name = taggedUser.display_name

  updateVipName(id, name)

  data = getVipData(id)

  await sendVipInfo(ctx, name, data)


# !cleanVips
@bot.command(name='cleanVips')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def cleanVips(ctx):
  expiredUsers = removeExpiredVips()
  userCount = len(expiredUsers)

  if expiredUsers:
    for id in expiredUsers:
      user = ctx.message.guild.get_member(int(id))
      if user:
        role = get(ctx.message.author.guild.roles, id=VIP_ROLE_ID)
        await user.remove_roles(role)

  if userCount > 0:
    await ctx.send('Cleaned ' + str(userCount) + ' user(s)')
  else:
    await ctx.send('No expired users found')

#@bot.command(name='dm')
@aiocron.crontab(CRON_SCHEDULE)
async def vipCron():

  guild = await bot.fetch_guild(SERVER_ID)

  # Clean up expired Vips

  expiredUsers = removeExpiredVips()
  removedUsers = []

  if expiredUsers:
    for expiredUser in expiredUsers:
      user = await guild.fetch_member(expiredUser['discordId'])
      if user:
        role = get(guild.roles, id=VIP_ROLE_ID)
        await user.remove_roles(role)

        # DM the user
        embed=discord.Embed(title="VIP EXPIRED", description="Your VIP Status at The Crimson Lotus has expired. Please come to the venue on our next opening to resubscribe so that you can keep all of your perks. ", color=CRIMLO_COLOR)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/629857962239852593/940494143728259072/LotusLogoFilled.png")
        embed.add_field(name="Name", value=expiredUser['name'], inline=False)
        embed.add_field(name="Start Date", value=expiredUser['startDate'], inline=False)
        embed.add_field(name="End Date", value=expiredUser['endDate'], inline=False)
        embed.set_footer(text="Thank you for being one of our valued patrons. If you have any questions please contact Patchwerk#0001 on Discord.")

        await user.send(embed=embed)

        removedUsers.append(user.display_name)

  # Log the report to the specified channel

  logChannel = bot.get_channel(CRON_CHANNEL_ID)

  embed = discord.Embed(title='Crimlo Bot Scheduled Report', color=CRIMLO_COLOR)
  embed.add_field(name='Date', value=date.today().strftime('%m/%d/%Y'))

  if removedUsers:
    embed.add_field(name='Removed and DM\'d the Following Users', value= '\n'.join(removedUsers), inline=False)

  await logChannel.send(embed=embed)

# Start bot
bot.run(BOT_TOKEN)
