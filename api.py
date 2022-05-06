import os
import requests

from util import getCurrentDate
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_HOST = os.getenv('API_HOST')

# Get data for a specific user by discord id
def getVipData(discordId: str):
  params = {
    'key': API_KEY,
    'discord_id': discordId
  }

  response = requests.get(url=API_HOST, params=params)
  data = response.json()

  if data.get('error'):
    return

  print(datetime.strptime(data.get('vip_expiration'), '%Y-%m-%d %H:%M:%S'))
  print(getCurrentDate())

  daysRemaining = max((datetime.strptime(data.get('vip_expiration'), '%Y-%m-%d %H:%M:%S').date() - getCurrentDate()).days, 0)

  return {
    'name': data['name'],
    'world': data['home_world'],
    'daysRemaining': daysRemaining
  }

# Add given number of vip months to a user
def addVipMonths(name, discordId, months: int):
  days = 30 * months

def getExpiredVips():
  return 0
