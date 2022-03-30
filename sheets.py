import os
import datetime as dt
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

cnx = mysql.connector.connect(
  user = os.getenv('DB_USER'),
  password = os.getenv('DB_PASSWORD'),
  host = os.getenv('DB_HOST'),
  port = os.getenv('DB_PORT'),
  database = os.getenv('DB_NAME')
)

cursor = cnx.cursor()

# Get data for a specific user by discord id
def getVipData(discordId: str):
  query = ("SELECT"
               "name,"
               "home_world AS 'homeWorld',"
               "DATEDIFF(vip_expiration, CURRENT_TIMESTAMP()) AS 'daysRemaining',"
               "vip_balance AS 'balance'"
             "FROM Players"
             "WHERE"
               "discord_id = %s"
               "AND vip_expiration > CURRENT_TIMESTAMP()")
  values = cursor.execute(query, (discordId))

  if not values:
    return

  return values[0]

# Add given number of vip months to a user
def addVipMonths(name, discordId, months: int):
  days = 30 * months

  # See if the user's discord id already exists in the table
  idQuery = ("SELECT id"
             "FROM Players"
             "WHERE"
               "discord_id = %s"
               "AND vip_expiration > CURRENT_TIMESTAMP()")
  idResult = cursor.execute(idQuery, (discordId))

  if idResult:

     # If the discord id exists in the table, update that row
    updateQuery = ('UPDATE Players'
                   'SET'
                     'vip_expiration = ('
                       'CASE'
                         'WHEN vip_expiration IS NULL OR vip_expiration < CURRENT_TIMESTAMP() THEN DATE_ADD(CURRENT_TIMESTAMP, INTERVAL %s MONTH)'
                         'ELSE DATE_ADD(vip_expiration, INTERVAL %s MONTH)'
                       'END'
                     '),'
                     'notified = 0'
                   'WHERE discord_id = %s')

    cursor.execute(updateQuery, (months, months, discordId))
  #TODO: If the discord id doesn't exist, check for the user's name
  #TODO: If the user's name exists, we need to ask which server - either way we need the server
  else:
    # Insert a new record
    #TODO: Get their home world
    #TODO: vip_balance?
    insertQuery = ('INSERT INTO Players (name, home_world, discord_id, vip_expiration, notified)'
                   'VALUES ('
                     '%s,'
                     '%s,'
                     '%s,'
                     'CASE'
                       'WHEN vip_expiration IS NULL OR vip_expiration < CURRENT_TIMESTAMP() THEN DATE_ADD(CURRENT_TIMESTAMP, INTERVAL %s MONTH)'
                       'ELSE DATE_ADD(vip_expiration, INTERVAL %s MONTH)'
                     'END,'
                     '0'
                   ')')
    cursor.execute(insertQuery, (name, 'Fake Home World', discordId, months, months))

def getExpiredVips():
  query = ("SELECT discord_id AS 'discordId'"
           "FROM Players"
           "WHERE"
             "vip_expiration < CURRENT_TIMESTAMP()"
             "AND notified = 0")

  return cursor.execute(query)
