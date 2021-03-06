import os

from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def getCurrentDate():
  return datetime.now(timezone.utc).date()

def getWorlds():
  return [
    'Adamantoise',
    'Cactuar',
    'Faerie',
    'Gilgamesh',
    'Jenova',
    'Midgardsormr',
    'Sargatanas',
    'Siren'
  ]
