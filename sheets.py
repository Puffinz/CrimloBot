import os
import datetime as dt

from datetime import date, datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

load_dotenv()

VIP_SHEET_ID = os.getenv('VIP_SHEET_ID')

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

# Clear a range in a given sheet
def clearInSheet(sheetId: str, range: str):
  sheet = buildService().spreadsheets()

  return sheet.values().clear(spreadsheetId=sheetId, range=range).execute()

# Get data from the vip spreadsheet
def getVipData(id: str):
  values = readSheet(VIP_SHEET_ID, 'A5:E')

  if not values:
    return

  for row in values:
    if len(row) > 1 and str(row[1]) == str(id):
      return {
        'name': row[0],
        'discordId': row[1],
        'startDate': row[2],
        'endDate': row[3],
        'remainingDays': row[4]
      }

  return None

# Add new row to the vip spreadsheet
def addVipMonth(name, id):
  values = readSheet(VIP_SHEET_ID, 'A5:E')

  # See if the name is already in the sheet
  userIndex = None
  data = None
  if values:
    for index, row in enumerate(values, start=0):
      if len(row) > 1 and str(row[1]) == str(id):
        userIndex = index
        data = {
          'name': row[0],
          'discordId': row[1],
          'startDate': row[2],
          'endDate': row[3],
          'remainingDays': row[4]
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

    dataArray = [name, str(data['discordId']), startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

    updateSheet(VIP_SHEET_ID, range, dataArray)
  else:
    startDate = date.today()
    endDate = startDate + dt.timedelta(days=30)

    dataArray = [name, str(id), startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

    appendToSheet(VIP_SHEET_ID, 'A5:D', dataArray)

# Update a user's name in the sheet for the given id
def updateVipName(id, name):
  values = readSheet(VIP_SHEET_ID, 'B5:B')

  # Find the id in the sheet
  userIndex = None
  if values:
    for index, row in enumerate(values, start=0):
      if len(row) > 0 and str(row[0]) == str(id):
        userIndex = index

  if userIndex:
    rowIndex = 5 + userIndex
    range = 'A' + str(rowIndex)

    updateSheet(VIP_SHEET_ID, range, [name])

def removeExpiredVips():
  values = readSheet(VIP_SHEET_ID, 'A5:E')

  removed = []

  if values:
    for index, row in enumerate(values, start=0):
      if len(row) > 4 and int(row[4]) <= 0:
        # Insert in the history table
        dataArray = row
        dataArray.append(date.today().strftime('%m/%d/%Y'))

        appendToSheet(VIP_SHEET_ID, 'HISTORY!A5:F', dataArray)

        # Remove from the main table
        rowIndex = 5 + index
        range = 'A' + str(rowIndex) + ':' + str(rowIndex)

        clearInSheet(VIP_SHEET_ID, range)

        removed.append(row[1])

  return removed
