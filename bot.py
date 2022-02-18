import os
import discord
import aiocron

from discord.ext import commands
from discord.utils import get
from discord.errors import NotFound
from dotenv import load_dotenv
from exceptions import GoogleAPIException, SheetException
from sheets import getVipData, addVipMonths, updateVipName, removeExpiredVips
from util import getCurrentDate

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

async def handleErrors(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('You must include a tagged user.', delete_after=5)
  elif isinstance(error, commands.MissingPermissions):
    return
  else:
    print(error)

async def sendVipInfo(ctx, user: discord.Member, data):
  if data:
    embed = discord.Embed(title='Crimson Lotus VIP Status', color=CRIMLO_COLOR)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name='Name', value=data['name'], inline=False)
    embed.add_field(name='Start Date', value=data['startDate'], inline=False)
    embed.add_field(name='End Date', value=data['endDate'], inline=False)
    embed.add_field(name='Days Remaining ', value=data['remainingDays'], inline=False)

    await ctx.send(embed=embed)
  else:
    await ctx.send('No vip data found for: ' + user.display_name)

# !help
bot.remove_command('help') # Remove the default help command
@bot.command(name='help')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def help(ctx):
  embed = discord.Embed(title = 'Help', color=CRIMLO_COLOR)

  embed.add_field(name=BOT_PREFIX + 'vip', value='Return vip information for your user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'getVip @<user>', value='Return vip information of the specified user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'addVip @<user>', value='Grant 1 month of vip to the specified user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'cleanVips', value='Manually run the scheduled cleanup task', inline=False)
  embed.add_field(name=BOT_PREFIX + 'renameVip @<user>', value='Update the name of an existing vip - use this if a vip has changed their discord name', inline=False)

  await ctx.send(embed=embed)

# !vip
@bot.command(name='vip')
async def vip(ctx):
  user = ctx.message.author

  try:
    data = getVipData(user.id)

    await sendVipInfo(ctx, user, data)
  except (SheetException, GoogleAPIException) as e:
    await reportError(e.message)

@vip.error
async def vip_error(ctx, error):
  await handleErrors(ctx, error)

# !getVip
@bot.command(name='getVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def getVip(ctx, taggedUser: discord.User):
  try:
    data = getVipData(taggedUser.id)

    await sendVipInfo(ctx, taggedUser, data)
  except (SheetException, GoogleAPIException) as e:
    await reportError(e.message)

@getVip.error
async def getVip_error(ctx, error):
  await handleErrors(ctx, error)

# !addVip
@bot.command(name='addVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def addVip(ctx, taggedUser: discord.Member, months = 1):
  name = taggedUser.display_name
  id = taggedUser.id

  try:
    addVipMonths(name, id, months)

    # Add VIP role
    role = get(ctx.message.author.guild.roles, id=VIP_ROLE_ID)
    await taggedUser.add_roles(role)

    data = getVipData(id)

    await sendVipInfo(ctx, taggedUser, data)
  except (SheetException, GoogleAPIException) as e:
    await reportError(e.message)

@addVip.error
async def addVip_error(ctx, error):
  await handleErrors(ctx, error)

# !renameVip
@bot.command(name='renameVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def renameVip(ctx, taggedUser: discord.Member):
  id = taggedUser.id
  name = taggedUser.display_name

  try:
    updateVipName(id, name)

    data = getVipData(id)

    await sendVipInfo(ctx, taggedUser, data)
  except (SheetException, GoogleAPIException) as e:
    await reportError(e.message)

async def reportError(errorMessage: str):
  logChannel = bot.get_channel(CRON_CHANNEL_ID)
  await logChannel.send(errorMessage)

@renameVip.error
async def renameVip_error(ctx, error):
  await handleErrors(ctx, error)

# !cleanVips
@bot.command(name='cleanVips')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def cleanVipsCommand(ctx):
  await cleanVips(True)

# Cron scheduled task
@aiocron.crontab(CRON_SCHEDULE)
async def vipCron():
  await cleanVips()

# Vip Cleaning
async def cleanVips(manual = False):

  guild = await bot.fetch_guild(SERVER_ID)

  # Clean up expired Vips

  expiredUsers = None
  error = False

  try:
    expiredUsers = removeExpiredVips()
  except (SheetException, GoogleAPIException) as e:
    error = e.message

  removedUsers = []
  notFoundUsers = []

  if expiredUsers:
    for expiredUser in expiredUsers:
      try:
        user = await guild.fetch_member(expiredUser['discordId'])
        if user:
          role = get(guild.roles, id=VIP_ROLE_ID)
          await user.remove_roles(role)

          # DM the user
          embed=discord.Embed(title='VIP EXPIRED', description='Your VIP Status at The Crimson Lotus has expired. Please come to the venue on our next opening to resubscribe so that you can keep all of your perks. ', color=CRIMLO_COLOR)
          embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/629857962239852593/940494143728259072/LotusLogoFilled.png')
          embed.add_field(name='Name', value=expiredUser['name'], inline=False)
          embed.add_field(name='Start Date', value=expiredUser['startDate'], inline=False)
          embed.add_field(name='End Date', value=expiredUser['endDate'], inline=False)
          embed.set_footer(text='Thank you for being one of our valued patrons. If you have any questions please contact Patchwerk#0001 on Discord.')

          await user.send(embed=embed)

          removedUsers.append(user.display_name)
      except (NotFound):
        notFoundUsers.append(expiredUser['name'])

  # Log the report to the specified channel

  logChannel = bot.get_channel(CRON_CHANNEL_ID)

  if manual:
    title = 'Crimlo Bot Manual Report'
  else:
    title = 'Crimlo Bot Scheduled Report'

  embed = discord.Embed(title=title, color=CRIMLO_COLOR)
  embed.add_field(name='Date', value=getCurrentDate().strftime('%m/%d/%Y'))

  if removedUsers:
    embed.add_field(name='Removed and DM\'d the Following Users', value='\n'.join(removedUsers), inline=False)

  if notFoundUsers:
    embed.add_field(name='Failed to change the role and DM the following expired users, which could not be found', value='\n'.join(notFoundUsers), inline=False)

  if error:
    embed.description = 'There were issues running the scheduled job, review the posted errors and the spreadsheet, then run !cleanVips manually'
    embed.add_field(name='Error', value=error, inline=False)

  await logChannel.send(embed=embed)

# Start bot
bot.run(BOT_TOKEN)
