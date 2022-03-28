import os
import datetime as dt
import mysql.connector

from dotenv import load_dotenv
from util import getCurrentDate

load_dotenv()

cnx = mysql.connector.connect(
  user = os.getenv('DB_USER'),
  password = os.getenv('DB_PASSWORD'),
  host = os.getenv('DB_HOST'),
  database = os.getenv('DB_NAME')
)

cursor = cnx.cursor()

# Get data for a specific user by discord id
def getVipData(discordId: str):
  query = 'SELECT name, home_world, vip_expiration, vip_balance WHERE discord_id = %s AND vip_tier = 1'
  values = cnx.execute(query, (discordId))

  if not values:
    return

  return values[0]

# Add given number of vip months to a user
def addVipMonths(name, discordId, months: int):
  days = 30 * months

  # See if the user's discord id already exists in the table
  idQuery = 'SELECT id WHERE discord_id = %s and vip_tier = 1'
  idResult = cnx.execute(valuesFromIdQuery, (discordId))

  # If the discord id exists, update that row
  if idResult:
    updateQuery = ()

  # If the discord id doesn't exist, check for the user's name

  # If the user's name exists, we need to ask which server - either way we need the server

  # See if the id or name is already in the sheet
  userIndex = None
  data = None
  if valuesFromId:
    for index, row in enumerate(values, start = 0):
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
      startDate = getCurrentDate()
      endDate = startDate + dt.timedelta(days=days)

    dataArray = [name, str(data['discordId']), startDate.strftime('%m/%d/%Y'), endDate.strftime('%m/%d/%Y')]

    updateSheet(VIP_SHEET_ID, range, dataArray)
  else:
    startDate = getCurrentDate()
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
        dataArray.append(getCurrentDate().strftime('%m/%d/%Y'))

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
