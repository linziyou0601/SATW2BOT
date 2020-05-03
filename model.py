import pytz, json, mysql.connector
from datetime import datetime

from env import *

def getMydb():
    mydb = mysql.connector.connect(
        host = ENV("DB_HOST"),
        user = ENV("DB_USER"),
        passwd = ENV("DB_PASSWORD"),
        database = ENV("DB_DATABASE")
    )
    mydb.autocommit = True
    return mydb

def operateDB(query, values):
    create_table()
    mydb = getMydb()
    cursor = mydb.cursor()
    cursor.execute(query, values) if values else cursor.execute(query)
    id = cursor.lastrowid if "INSERT" in query else None
    cursor.close()
    mydb.close()
    return id

def selectDB(query, values):
    create_table()
    mydb = getMydb()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(query, values) if values else cursor.execute(query)
    data_rows = cursor.fetchall()
    cursor.close()
    mydb.close()
    return data_rows

def create_table():
    query = ENV("DB_CREATE_TABLE", "")
    mydb = getMydb()
    cursor = mydb.cursor()
    cursor.execute(query, multi=True)
    cursor.close()
    mydb.close()
