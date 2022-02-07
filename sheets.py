import os
import datetime as dt

from datetime import date, datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Build a google sheets api service with proper credentials
def buildService():
  scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
  credentials = service_account.Credentials.from_service_account_file('creds.json', scopes=scopes)

  return build('sheets', 'v4', credentials=credentials)

# Return values from given sheet at the specified range
def readSheet(sheetId: str, range: str):
  sheet = buildService().spreadsheets()

  result = sheet.values().get(spreadsheetId=sheetId, range=range).execute()

  return result.get('values', [])

# Add given values to the given sheet in the specified range
def appendToSheet(sheetId: str, range: str, values):
  body = {
    'range': range,
    'values': [values]
  }

  sheet = buildService().spreadsheets()

  return sheet.values().append(spreadsheetId=sheetId, range=range, valueInputOption='USER_ENTERED', insertDataOption='OVERWRITE', body=body).execute()

# Update given range in sheet with values
def updateSheet(sheetId: str, range: str, values):
  body = {
    'range': range,
    'values': [values]
  }

  sheet = buildService().spreadsheets()

  return sheet.values().update(spreadsheetId=sheetId, range=range, valueInputOption='USER_ENTERED', body=body).execute()

# Get data from the vip spreadsheet
def getVipData(name: str):
  values = readSheet(os.getenv('VIP_SHEET_ID'), 'A5:D')

  if not values:
    return

  for row in values:
    if len(row) > 0 and row[0].strip().lower() == name.strip().lower():
      return {
        'name': row[0],
        'startDate': row[1],
        'endDate': row[2],
        'remainingDays': row[3]
      }

  return None

# Add new row to the vip spreadsheet
def addVipMonth(name):
  values = readSheet(os.getenv('VIP_SHEET_ID'), 'A5:D')

  # See if the name is already in the sheet
  userIndex = None
  data = None
  if values:
    for index, row in enumerate(values, start=0):
      if len(row) > 0 and row[0].strip().lower() == name.strip().lower():
        userIndex = index
        data = {
          'name': row[0],
          'startDate': row[1],
          'endDate': row[2],
          'remainingDays': row[3]
        }

  if data:
    rowIndex = 5 + userIndex
    range = 'A' + str(rowIndex) + ':D' + str(rowIndex)
    if int(data['remainingDays']) > 0:
      startDate = datetime.strptime(data['startDate'], '%m/%d/%Y')
      endDate = datetime.strptime(data['endDate'], '%m/%d/%Y') + dt.timedelta(days=30)
    else:
      startDate = date.today()
      endDate = startDate + dt.timedelta(days=30)

    dataArray = [name, startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

    updateSheet(os.getenv('VIP_SHEET_ID'), range, dataArray)
  else:
    startDate = date.today()
    endDate = startDate + dt.timedelta(days=30)

    dataArray = [name, startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

    appendToSheet(os.getenv('VIP_SHEET_ID'), 'A5:C', dataArray)



