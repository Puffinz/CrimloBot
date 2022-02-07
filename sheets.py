import os
import datetime

from datetime import date
from googleapiclient.discovery import build
from google.oauth2 import service_account

def buildService():
  scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
  credentials = service_account.Credentials.from_service_account_file('creds.json', scopes=scopes)

  return build('sheets', 'v4', credentials=credentials)

def readSheet(sheetId: str, range: str):
  sheet = buildService().spreadsheets()

  result = sheet.values().get(spreadsheetId=sheetId, range=range).execute()

  return result.get('values', [])

def appendToSheet(sheetId :str, range: str, values):
  body = {
    'range': range,
    'values': [values]
  }

  sheet = buildService().spreadsheets()

  return sheet.values().append(spreadsheetId=sheetId, range=range, valueInputOption='USER_ENTERED', insertDataOption='OVERWRITE', body=body).execute()


def getVipData(name: str):
  values = readSheet(os.getenv('VIP_SHEET_ID'), 'A5:D')

  if not values:
    return

  for row in values:
    if row[0].strip().lower() == name.strip().lower():
      return {
        'name': row[0],
        'startDate': row[1],
        'endDate': row[2],
        'remainingDays': row[3]
      }
  
  return None

def grantVipMonth(name: str):
  data = getVipData(name)

def addVipData(name: str):
  startDate = date.today()
  endDate = startDate + datetime.timedelta(days=30)

  dataArray = [name, startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

  appendToSheet(os.getenv('VIP_SHEET_ID'), 'A5:C', dataArray)
