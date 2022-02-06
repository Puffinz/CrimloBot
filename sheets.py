import os

from googleapiclient.discovery import build

def readSheet(sheetId: str, range: str):
  service = build('sheets', 'v4', developerKey=os.getenv('GOOGLE_API_KEY'))

  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=sheetId, range=range).execute()

  return result.get('values', [])

def getVipData(name: str):
  values = readSheet(os.getenv('VIP_SHEET_ID'), os.getenv('VIP_SHEET_RANGE'))

  if not values:
    print('No vip data found.')
    return

  for row in values:
    if row[0].strip().lower() == name.strip().lower():
      return {
        'name': row[0],
        'tier': row[1],
        'startDate': row[2],
        'endDate': row[3],
        'remainingDays': row[4]
      }
  
  return None
