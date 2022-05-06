import os
import pytz

from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

TIMEZONE = os.getenv('TIMEZONE') or 'Etc/UTC'

def getCurrentDate():
  return datetime.now(pytz.timezone(TIMEZONE)).date()
