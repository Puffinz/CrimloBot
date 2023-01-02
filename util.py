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
    'Siren',
    'Balmung',
    'Brynhildr',
    'Coeurl',
    'Diabolos',
    'Goblin',
    'Malboro',
    'Mateus',
    'Zalera',
    'Behemoth',
    'Excalibur',
    'Exodus',
    'Famfrit',
    'Hyperion',
    'Lamia',
    'Leviathan',
    'Ultros',
    'Halicarnassus',
    'Maduin',
    'Marilith',
    'Seraph'
  ]
