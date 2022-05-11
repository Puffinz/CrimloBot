import os
import requests

from util import getCurrentDate
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LIFETIME_STRING = 'lifetime'
LIFETIME_DATE_INPUT = '9999-01-01'
LIFETIME_DATE_OUTPUT = '9998-12-31 17:00:00'

# Get a user or add vip time
def existingUserRequest(discordId, months: str = '0'):
  params = {
    'discord_id': discordId
  }

  if (months.strip().lower() == LIFETIME_STRING):
    params['setvipdate'] = LIFETIME_DATE_INPUT
  else:
    params['addmonth'] = months

  return userRequest(params)

# Create a new vip user
def newUserRequest(discordId, name, world, months: str = '0'):
  params = {
    'set_discord_id': discordId,
    'addmonth': months,
    'name': name + '@' + world,
    'create': '1'
  }

  if (months.strip().lower() == LIFETIME_STRING):
    params['setvipdate'] = LIFETIME_DATE_INPUT
  else:
    params['addmonth'] = months

  return userRequest(params)

# Generic request that returns data for a single user
def userRequest(params):
  data = apiRequest(params)

  if data.get('error'):
    return

  expiration = data.get('vip_expiration')
  if expiration == LIFETIME_DATE_OUTPUT:
    daysRemaining = 'Lifetime'
  elif expiration:
    daysRemaining = max((datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S').date() - getCurrentDate()).days, 0)
  else:
    daysRemaining = 0

  return {
    'name': data['name'],
    'world': data['home_world'],
    'daysRemaining': daysRemaining
  }

# Get a list of all discord ids that currently have vip
def getAllVips():
  params = {
    'get_vips': 1
  }

  data = apiRequest(params)

  if data.get('error'):
    return

  vipList = []
  for user in data['vip_users']:
    vipList.append(int(user['discord_id']))

  return vipList

# Generic api request
def apiRequest(params):
  params['key'] = os.getenv('API_KEY')

  response = requests.get(url=os.getenv('API_HOST'), params=params)
  data = response.json()

  return data
