import os
import discord
import aiocron

from discord.ext import commands
from discord.utils import get
from discord.errors import NotFound
from dotenv import load_dotenv
from util import getCurrentDate, getWorlds
from api import existingUserRequest, newUserRequest, getAllVips

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
    await ctx.send('Missing required parameter. Use the help command for more info.', delete_after=5)
  elif isinstance(error, commands.MissingPermissions):
    return
  else:
    print(error)

async def sendVipInfo(ctx, user: discord.Member, data):
  if data:
    embed = discord.Embed(title='Crimson Lotus VIP Status', color=CRIMLO_COLOR)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name='Name', value=data['name'], inline=False)
    embed.add_field(name='World', value=data['world'], inline=False)
    embed.add_field(name='Days Remaining ', value=data['daysRemaining'], inline=False)

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
  embed.add_field(name=BOT_PREFIX + 'newVip @<user> <world> <months (optional)>', value='Add a new user to the system, and grant them month(s) of vip', inline=False)
  embed.add_field(name=BOT_PREFIX + 'addVip @<user> <months (optional)>', value='Grant month(s) of vip to the specified user', inline=False)
  embed.add_field(name=BOT_PREFIX + 'cleanVips', value='Manually run the scheduled cleanup task', inline=False)

  await ctx.send(embed=embed)

# !vip
@bot.command(name='vip')
async def vip(ctx):
  user = ctx.message.author

  data = existingUserRequest(user.id)

  await sendVipInfo(ctx, user, data)

@vip.error
async def vip_error(ctx, error):
  await handleErrors(ctx, error)

# !getVip
@bot.command(name='getVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def getVip(ctx, taggedUser: discord.User):
  data = existingUserRequest(taggedUser.id)

  await sendVipInfo(ctx, taggedUser, data)

@getVip.error
async def getVip_error(ctx, error):
  await handleErrors(ctx, error)

# !newVip
@bot.command(name='newVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def newVip(ctx, taggedUser: discord.Member, world: str, months = 1):
  id = taggedUser.id

  oldData = existingUserRequest(id)

  if oldData:
    await ctx.send('User already exists in the system.')

  else:
    name = taggedUser.display_name

    world = world.title() #Capitalize properly
    if world in getWorlds():
      newData = newUserRequest(id, name, world, months)

      if newData:
        # Add VIP role
        role = get(ctx.message.author.guild.roles, id=VIP_ROLE_ID)
        await taggedUser.add_roles(role)

      await sendVipInfo(ctx, taggedUser, newData)
    else:
      await ctx.send('The world entered does not exist on the Aether data center.')

@newVip.error
async def newVip_error(ctx, error):
  await handleErrors(ctx, error)

# !addVip
@bot.command(name='addVip')
@commands.has_role(BOT_MANAGER_ROLE_ID)
async def addVip(ctx, taggedUser: discord.Member, months = 1):
  id = taggedUser.id

  data = existingUserRequest(id, months)

  if data:
    # Add VIP role
    role = get(ctx.message.author.guild.roles, id=VIP_ROLE_ID)
    await taggedUser.add_roles(role)

  await sendVipInfo(ctx, taggedUser, data)

@addVip.error
async def addVip_error(ctx, error):
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
  role = get(guild.roles, id=VIP_ROLE_ID)

  removedUsers = []
  notFoundUsers = []

  existingVipIds = getAllVips()

  # Loop through all members of the discord
  async for member in guild.fetch_members(limit=None):
    # Check if the user has the vip role
    if role in member.roles:
      if member.id not in existingVipIds:
        # Get data from the api
        data = existingUserRequest(member.id)

        if data:
          await member.remove_roles(role)

          # DM the user
          embed=discord.Embed(title='VIP EXPIRED', description='Your VIP Status at The Crimson Lotus has expired. Please come to the venue on our next opening to resubscribe so that you can keep all of your perks. ', color=CRIMLO_COLOR)
          embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/629857962239852593/940494143728259072/LotusLogoFilled.png')
          embed.add_field(name='Name', value=data['name'], inline=False)
          embed.add_field(name='World', value=data['world'], inline=False)
          embed.add_field(name='Days Remaning', value='0', inline=False)
          embed.set_footer(text='Thank you for being one of our valued patrons. If you have any questions please contact Patchwerk#0001 on Discord.')

          await member.send(embed=embed)

          removedUsers.append(member.display_name)
        else:
          # User is not found by the api, add the the report
          notFoundUsers.append(member.display_name)


  # Log the report to the specified channel

  logChannel = bot.get_channel(CRON_CHANNEL_ID)

  if manual:
    title = 'Crimlo Bot Manual Report'
  else:
    title = 'Crimlo Bot Scheduled Report'

  embed = discord.Embed(title=title, color=CRIMLO_COLOR)
  embed.add_field(name='Date', value=getCurrentDate().strftime('%m/%d/%Y'))

  if removedUsers:
    embed.add_field(name='I have removed the vip role from and sent a direct message to the following users:', value='\n'.join(removedUsers), inline=False)

  if notFoundUsers:
    embed.add_field(name='These users have the vip role but were not found in system - please review manually:', value='\n'.join(notFoundUsers), inline=False)

  await logChannel.send(embed=embed)

# Start bot
bot.run(BOT_TOKEN)
