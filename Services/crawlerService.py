##########爬蟲、資料取得##########
from datetime import datetime, timedelta
from urllib.parse import quote
import os, sys, pytz, urllib.request, requests, csv, json, math, string
import numpy as np

#前往上層目錄
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
#導入Others
from Others.flexMessageJSON import *
#導入Controllers
from Controllers.normalController import *
from Controllers.chatterController import *
#導入Services
from Services.geocodingService import *

GEOCODING_API_KEY = GET_SECRET("Geocoding API")

## 取得天氣資訊
def getWeather(lat, lng, site, future=False):
    #=========================== 取得所有測站資料 [↓] ===========================#
    with urllib.request.urlopen("https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-268DE0E2-66E8-4AE9-A0C3-B06F7EBB5E7A&format=JSON&elementName=TEMP,HUMD,H_24R") as url1:
        with urllib.request.urlopen("https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWB-268DE0E2-66E8-4AE9-A0C3-B06F7EBB5E7A&elementName=TEMP,HUMD,24R") as url2:
            with urllib.request.urlopen("https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-089?Authorization=CWB-268DE0E2-66E8-4AE9-A0C3-B06F7EBB5E7A&elementName=Wx,T,CI,PoP6h") as url72:
                #讀取天氣資料
                obj1 = json.loads(url1.read().decode())['records']['location']                      #自動氣象站           
                obj2 = json.loads(url2.read().decode())['records']['location']                      #局屬氣象站
                obj72 = json.loads(url72.read().decode())['records']['locations'][0]['location']    #72小時天氣
                #暫存天氣物件
                weatherALL_info = []       #所有測站資訊
                weatherALL_location = []   #所有測站經緯度
                for row in obj1+obj2:
                    dt = datetime.strptime(row['time']['obsTime']+'.000000', '%Y-%m-%d %H:%M:%S.%f').astimezone(pytz.timezone("Asia/Taipei"))
                    #取[經度,緯度]
                    lat_temp = float(row['lat'])
                    lng_temp = float(row['lon'])
                    #存[經度,緯度,測站資訊]
                    info = {
                        'locationName': row['locationName'],
                        'City': row['parameter'][0]['parameterValue'],
                        'Town': row['parameter'][2]['parameterValue'],
                        'TimeString': datetime.strftime(dt, '%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                        'Temp': row['weatherElement'][0]['elementValue'],
                        'Humd': row['weatherElement'][1]['elementValue'],
                        '24R': row['weatherElement'][2]['elementValue']
                    }
                    weatherALL_location.append([lat_temp, lng_temp])
                    weatherALL_info.append(info)
    #=========================== 取得所有測站資料 [↑] ===========================#

    #=========================== 取得資料 [↓] ===========================#
    ALL_LOCATION = get_all_location()   #取得已有紀錄的地址:經緯資訊
    if (not lat or not lng):
        if addr_format(site) in ALL_LOCATION:
            lat = ALL_LOCATION[addr_format(site)]["lat"]
            lng = ALL_LOCATION[addr_format(site)]["lng"]
        else:
            url = "https://maps.googleapis.com/maps/api/geocode/json?address="+addr_format(site)+"&key="+GEOCODING_API_KEY
            json_r = json.loads(requests.get(url).text)
            if json_r['status'] == "OK":
                location = json_r['results'][0]['geometry']['location']
                lat = location["lat"]
                lng = location["lng"]
                create_location(addr_format(site), lat, lng)
    if (lat and lng):
        find_loc = np.matrix([[lat, lng]])
        disALLDict = np_getDistance(np.matrix(weatherALL_location), find_loc, weatherALL_info)    # 全部距離+資料
        disAll = list(disALLDict.keys())                                                          # 全部距離
        disInfo = disALLDict[disAll[0]]                                                           # 取得最近的測站資料
    #=========================== 取得資料 [↑] ===========================#
    
    #=========================== 取得72小時資料 / 補上目前天氣缺的資料 / 並回傳 [↓] ===========================#
        data72Hours = get72Hours(obj72, disInfo['City'])       # 取得該測站72小時資料
        disInfo['Wx'] = data72Hours[0]['Wx']                   # 天氣現象
        disInfo['CI'] = data72Hours[0]['CI']                   # 舒適度
        disInfo['PoP6h'] = data72Hours[0]['PoP6h']             # 6小時降雨率
        
        return data72Hours if future else disInfo
    return {}
    #=========================== 取得72小時資料 / 補上目前天氣缺的資料 / 並回傳 [↑] ===========================#

## 取得72小時天氣資訊
def get72Hours(obj72, location):
    result = []
    for row in obj72:
        if any((location in s) or (s in location) for s in [row['locationName'], row['locationName'][0:2]]):
            for i in range(10):
                st_dt = datetime.strptime(row['weatherElement'][0]['time'][i]['startTime']+'.000000', '%Y-%m-%d %H:%M:%S.%f').astimezone(pytz.timezone("Asia/Taipei"))
                ed_dt = datetime.strptime(row['weatherElement'][0]['time'][i]['endTime']+'.000000', '%Y-%m-%d %H:%M:%S.%f').astimezone(pytz.timezone("Asia/Taipei"))
                result.append({
                    'locationName': row['locationName'],
                    'startTime': datetime.strftime(st_dt, '%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                    'endTime': datetime.strftime(ed_dt, '%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
                    'Wx': row['weatherElement'][0]['time'][i]['elementValue'][0]['value'],
                    'Temp': row['weatherElement'][1]['time'][i]['elementValue'][0]['value'],
                    'CI': row['weatherElement'][2]['time'][i]['elementValue'][1]['value'],
                    'PoP6h': row['weatherElement'][3]['time'][math.floor(i/2)]['elementValue'][0]['value']
                })
            if result: return result
    return []


## 取得空汙資訊
def getAQI(lat, lng, site):
    #=========================== 取得所有測站資料 [↓] ===========================#
    with urllib.request.urlopen("http://opendata.epa.gov.tw/webapi/Data/REWIQA/?$orderby=County&$skip=0&$top=1000&format=json") as url:
        obj = json.loads(url.read().decode())
        #暫存天氣物件
        aqiALL_info = []       #所有測站資訊
        aqiALL_location = []   #所有測站經緯度
        for row in obj:
            dt = datetime.strptime(row['PublishTime']+':00.000000', '%Y-%m-%d %H:%M:%S.%f').astimezone(pytz.timezone("Asia/Taipei"))
            #取[經度,緯度]
            lat_temp = float(row['Latitude'])
            lng_temp = float(row['Longitude'])
            #存[經度,緯度,測站資訊]
            row['timeStr'] = datetime.strftime(dt, '%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日')
            aqiALL_location.append([lat_temp, lng_temp])
            aqiALL_info.append(row)
    #=========================== 取得所有測站資料 [↑] ===========================#

    #=========================== 取得資料 [↓] ===========================#
    ALL_LOCATION = get_all_location()   #取得已有紀錄的地址:經緯資訊
    if (not lat or not lng):
        if addr_format(site) in ALL_LOCATION:
            lat = ALL_LOCATION[addr_format(site)]["lat"]
            lng = ALL_LOCATION[addr_format(site)]["lng"]
        else:
            url = "https://maps.googleapis.com/maps/api/geocode/json?address="+addr_format(site)+"&key="+GEOCODING_API_KEY
            json_r = json.loads(requests.get(url).text)
            if json_r['status'] == "OK":
                location = json_r['results'][0]['geometry']['location']
                lat = location["lat"]
                lng = location["lng"]
                create_location(addr_format(site), lat, lng)
    
    if (lat and lng):
        find_loc = np.matrix([[lat, lng]])
        disALLDict = np_getDistance(np.matrix(aqiALL_location), find_loc, aqiALL_info)    # 全部距離+資料
        disAll = list(disALLDict.keys())                                                  # 全部距離
        disInfo = disALLDict[disAll[0]]                                                   # 取得最近的測站資料
        return disInfo
    return {}
    #=========================== 取得資料 [↑] ===========================#

## 抽酷碰券
def draw_coupon():
    #=========================== 抽酷碰 [↓] ===========================#
    with urllib.request.urlopen("https://satw2.linziyou.info/api/generateCoupon") as url:
        obj = json.loads(url.read().decode())
        return obj
    #=========================== 抽酷碰 [↑] ===========================#

## 查詢商品
def getProducts(key=""):
    #=========================== 取得資料 [↓] ===========================#
    url = "https://satw2.linziyou.info/api/getProducts?key=" + str(key)
    url = quote(url, safe=string.printable)
    with urllib.request.urlopen(url) as url:
        obj = json.loads(url.read().decode())
        return obj
    #=========================== 取得資料 [↑] ===========================#