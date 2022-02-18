import os
import pytz

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TIMEZONE = os.getenv('TIMEZONE') or 'Etc/UTC'

def getCurrentDate():
  return datetime.utcnow().replace(tzinfo=pytz.timezone(TIMEZONE)).date()
