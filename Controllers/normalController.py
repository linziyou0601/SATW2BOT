import os, sys, json, codecs, re

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import *

#前往上層目錄
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
#導入env, model
from env import *
from model import *
#導入Others
from Others.flexMessageJSON import *

#################### 金鑰相關 ####################
#取得金鑰
def GET_SECRET(name):
    query = """SELECT * FROM api_key WHERE name = %s"""
    values = (name,)
    dataRow = selectDB(query, values)
    return dataRow[0]['secret'] if len(dataRow) else ""

#################### 使用者相關 ####################
#建立新使用者
def create_channel(channelId):
    if get_channel(channelId)==None:
        query = """INSERT INTO line_user (channel_id) VALUES (%s)"""
        values = (channelId,)
        operateDB(query, values)

#移除使用者
def remove_channel(channelId):
    query = """DELETE FROM line_user WHERE channel_id = %s"""
    values = (channelId,)
    operateDB(query, values)

#查詢使用者
def get_channel(channelId):
    query = """SELECT * FROM line_user WHERE channel_id = %s"""
    values = (channelId,)
    dataRow = selectDB(query, values)
    return dataRow[0] if len(dataRow) else None

#綁定帳號
def draw_coupon(channelId):
    query = """UPDATE line_user SET draw_coupon = %s where channel_id = %s"""
    values = (datetime.now(), channelId,)
    operateDB(query, values)

#綁定帳號
def bind_account(channelId, account):
    query = """UPDATE line_user SET account = %s, bind = 1 where channel_id = %s"""
    values = (account, channelId,)
    operateDB(query, values)

#解綁帳號
def unbind_account(channelId):
    query = """UPDATE line_user SET account = NULL, bind = 0 where channel_id = %s"""
    values = (channelId,)
    operateDB(query, values)

#################### 取得資料庫中的經緯資訊 ####################
#經緯資訊
def get_all_location():
    query = """SELECT address, lat, lng FROM line_location"""
    dataRow = selectDB(query, None)
    result_dict = {}
    if len(dataRow):
        for row in dataRow:
            result_dict[row['address']] = {'lat': row['lat'], 'lng': row['lng']}
    return result_dict
#經緯資訊
def get_location(location):
    query = """SELECT lat, lng FROM line_location WHERE address = %s"""
    dataRow = selectDB(query, (location,))
    return dataRow[0] if len(dataRow) else None
#建立經緯資訊
def create_location(address, lat, lng):
    if not get_location(address):
        query = """INSERT INTO line_location (address, lat, lng) VALUES (%s, %s, %s)"""
        values = (address, lat, lng,)
        operateDB(query, values)

#################### 訊息相關 ####################
##儲存收到的訊息
def store_received(msg, type, channelId, userId):
    query = """INSERT INTO line_received (type, message, channel_id, user_id) VALUES (%s,%s,%s,%s)"""
    values = (type, msg, channelId, userId,)
    operateDB(query, values)

##儲存機器人回覆
def store_replied(msg, valid, type, channelId):
    query = """INSERT INTO line_replied (type, message, valid, channel_id) VALUES (%s,%s,%s,%s)"""
    values = (type, msg, valid, channelId,)
    operateDB(query, values)

##儲存收到的訊息
def store_pushed(type, title, message, channelId):
    query = """INSERT INTO line_pushed (type, title, message, channel_id) VALUES (%s,%s,%s,%s)"""
    values = (type, title, message, channelId,)
    operateDB(query, values)

##查詢收到的訊息
def get_received(channelId, num):
    query = """SELECT * FROM line_received WHERE channel_id=%s ORDER BY id DESC limit %s"""
    values = (channelId, num,)
    dataRow = selectDB(query, values)
    return dataRow if len(dataRow) else []

##查詢機器人回覆
def get_replied(channelId, num):
    query = """SELECT * FROM line_replied WHERE channel_id=%s ORDER BY id DESC limit %s"""
    values = (channelId, num,)
    dataRow = selectDB(query, values)
    return dataRow if len(dataRow) else []

#################### 推播相關 ####################
line_bot_api = LineBotApi(GET_SECRET("ACCESS_TOKEN"))

#一般推播處理
def pushing_process(type, title, content, channelId):

    message = []
    record = ''
    if type == 'text':
        message = TextSendMessage(text='【' + title + '】\n' + content)
        record = content
    elif type == 'flex':
        try:
            obj = json.loads(content)
            message = FlexSendMessage(alt_text=title, contents=obj)
            record = json.dumps(obj)
        except:
            return 'fail'
    elif type == 'image':
        if 'https://' in content and any(x in content for x in ['.jpg','.jpeg','.png']):
            message = ImageSendMessage(original_content_url=content, preview_image_url=content)
            record = content
        else:
            return 'fail'

    return pushing_to_channel(type, title, message, channelId, record)

#樣板推播處理
def pushing_template(title, content, channelId, template):
    message = []
    type = "flex"
    obj = content
    record = ''
    if template == "announcement":
        try:
            message = FlexSendMessage(alt_text=title, contents=templateAnnouncement(obj.get('title', ''), obj.get('content', ''), obj.get('date', '')))
            record = json.dumps(templateAnnouncement(obj.get('title', ''), obj.get('content', ''), obj.get('date', '')))
        except:
            return 'fail'
    
    return pushing_to_channel(type, title, message, channelId, record)

#發送推播
def pushing_to_channel(type, title, message, channel_id, record):
    try:
        if channel_id!=None:
            if channel_id=="ALL": pushing_to_all(type, title, message, record)  #廣播
            else: line_bot_api.push_message(channel_id, message)                #推播
        store_pushed(type, title, record, channel_id)
        return 'ok'
    except:
        return 'fail'

#發送廣播
def pushing_to_all(type, title, message, record):
    try:
        query = """SELECT channel_id FROM line_user"""
        dataRow = selectDB(query, None)
        datas = dataRow if len(dataRow) else []
        for data in datas:
            line_bot_api.push_message(data["channel_id"], message)
        store_pushed(type, title, record, "ALL")
        return 'ok'
    except:
        return 'fail'