import os
import datetime as dt

from datetime import date
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
from exceptions import GoogleAPIException, SheetException
from httplib2 import ServerNotFoundError
from json import JSONDecodeError

load_dotenv()

VIP_SHEET_ID = os.getenv('VIP_SHEET_ID')
VIP_USER_CLOSE_TO_EXPIRY = os.getenv('VIP_USER_CLOSE_TO_EXPIRY_DAYS')

# Build a google sheets api service with proper credentials
def buildService():
  scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]

  try:
    credentials = service_account.Credentials.from_service_account_file('creds.json', scopes=scopes)
  except ServerNotFoundError:
    raise GoogleAPIException

  return build('sheets', 'v4', credentials=credentials)

# Return values from given sheet at the specified range
def readSheet(sheetId: str, range: str):
  sheet = buildService().spreadsheets()

  try:
    result = sheet.values().get(spreadsheetId=sheetId, range=range, valueRenderOption='UNFORMATTED_VALUE').execute()
  except JSONDecodeError:
    raise GoogleAPIException

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

# Get pageId for given pageName
def getPageId(sheetId: str, pageName: str):
  sheet = buildService().spreadsheets()

  pageId = None
  spreadsheets = sheet.get(spreadsheetId=sheetId).execute()
  for page in spreadsheets['sheets']:
    if page['properties']['title'] == pageName:
      pageId = page['properties']['sheetId']

  return pageId

# Delete a single row from a sheet on a given page
def deleteRow(sheetId: str, pageId: int, rowIndex: int):
  sheet = buildService().spreadsheets()

  body = {
    'requests': {
      'deleteDimension': {
        'range': {
          'sheetId': pageId,
          'dimension': 'ROWS',
          'startIndex': rowIndex - 1,
          'endIndex': rowIndex
        }
      }
    }
  }

  sheet.batchUpdate(spreadsheetId=sheetId, body=body).execute()

# Get data from the vip spreadsheet
def getVipData(id: str):
  values = readSheet(VIP_SHEET_ID, 'A5:E')

  if not values:
    return

  for row in values:
    if len(row) > 1 and str(row[1]) == str(id):
      return rowToVipMap(row, True)

  return None

# Add given number of months to vip in spreadsheet
def addVipMonths(name, id, months: int):
  days = 30 * months
  values = readSheet(VIP_SHEET_ID, 'A5:E')

  # See if the name is already in the sheet
  userIndex = None
  data = None
  if values:
    for index, row in enumerate(values, start=0):
      if len(row) > 1 and str(row[1]) == str(id):
        userIndex = index
        data = rowToVipMap(row)

  if data:
    rowIndex = 5 + userIndex
    range = 'A' + str(rowIndex) + ':D' + str(rowIndex)
    if int(data['remainingDays']) > 0:
      startDate = data['startDate']
      endDate = data['endDate'] + dt.timedelta(days=days)
    else:
      startDate = date.today()
      endDate = startDate + dt.timedelta(days=days)

    dataArray = [name, str(data['discordId']), startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

    updateSheet(VIP_SHEET_ID, range, dataArray)
  else:
    startDate = date.today()
    endDate = startDate + dt.timedelta(days=days)

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
    rowsToDelete = []

    for index, row in enumerate(values, start=0):
      if len(row) > 4 and int(row[4]) <= 0:
        # Insert in the history table
        dataArray = row
        dataArray.append(date.today().strftime('%m/%d/%Y'))

        appendToSheet(VIP_SHEET_ID, 'HISTORY!A5:F', dataArray)

        removed.append(rowToVipMap(row))

        rowsToDelete.append(index + 5)

    pageId = getPageId(VIP_SHEET_ID, 'OVERALL')

    # Make sure the rows are sorted
    rowsToDelete.sort()

    for index, row in enumerate(rowsToDelete, start=0):
      # Remove the current place in the list from each row index.
      # This way they will be accurate after other rows are removed
      row -= index
      deleteRow(VIP_SHEET_ID, pageId, row)

  return removed

def convertXLSDateTime(date):
  return (dt.datetime(1899, 12, 30) + dt.timedelta(days=date))

def rowToVipMap(row, text = False):
  map = {}

  if len(row) > 0 and row[0] != None and row[0] != '':
    map['name'] = row[0]
  else:
    raise SheetException('A Name')

  if len(row) > 1 and row[1] != None and row[1] != '':
    map['discordId'] = row[1]
  else:
    raise SheetException('Discord ID', map['name'])

  if len(row) > 2 and row[2] != None and row[2] != '':
    try:
      map['startDate'] = convertXLSDateTime(row[2])
    except TypeError:
      raise SheetException('Start Date', map['name'])
    if text:
      map['startDate'] = map['startDate'].strftime('%m/%d/%Y')
  else:
    raise SheetException('Start Date', map['name'])

  if len(row) > 3 and row[3] != None and row[3] != '':
    try:
      map['endDate'] = convertXLSDateTime(row[3])
    except TypeError:
      raise SheetException('End Date', map['name'])
    if text:
      map['endDate'] = map['endDate'].strftime('%m/%d/%Y')
  else:
    raise SheetException('End Date', map['name'])

  if len(row) > 4:
    map['remainingDays'] = row[4]
  else:
    map['remainingDays'] = 0

  return map
