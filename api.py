import os
import requests

from util import getCurrentDate
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Get a user or add vip time
def existingUserRequest(discordId, months: int = 0):
  params = {
    'discord_id': discordId,
    'addmonth': months
  }

  return userRequest(params)

# Create a new vip user
def newUserRequest(discordId, name, world, months: int = 0):
  params = {
    'set_discord_id': discordId,
    'addmonth': months,
    'name': name + '@' + world,
    'create': '1'
  }

  print(params)

  return userRequest(params)

def userRequest(params):
  params['key'] = os.getenv('API_KEY')

  response = requests.get(url=os.getenv('API_HOST'), params=params)
  data = response.json()

  if data.get('error'):
    return

  daysRemaining = max((datetime.strptime(data['vip_expiration'], '%Y-%m-%d %H:%M:%S').date() - getCurrentDate()).days, 0)

  return {
    'name': data['name'],
    'world': data['home_world'],
    'daysRemaining': daysRemaining
  }

def getExpiredVips():
  return 0
