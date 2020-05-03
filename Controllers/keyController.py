import os, sys, json, codecs, re

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import *

#關鍵字正則（優先度：1）
regDict1 = {
    # [教學選單]
    "主選單": "^(主選單|樹懶(醬)?)$",
    "功能一覽": "^(你|樹懶(醬)?)?(會(做什麼|幹嘛)|有什麼功能)$",
    "怎麼聊天": "^(怎麼|如何)聊天|聊天教學$",
    "怎麼抽籤": "^(怎麼|如何)抽籤|抽籤教學$",
    #-----#
    "怎麼學說話": "^(怎麼|如何)(學說話|教你說話)|學說話教學$",
    "學過的話": "^(你|樹懶(醬)?)(會(說|講)什麼)$",
    "怎麼抽籤式回答": "^(怎麼|如何)(隨機|抽籤式)回答|抽籤式回答教學$",
    #-----#
    "怎麼查商品": "^(怎麼|如何)?查商品|查商品教學$",
    "怎麼查氣象": "^(怎麼|如何)?查氣象|查氣象教學$",
    "怎麼查天氣": "^(怎麼|如何)查天氣|查天氣教學$",
    "怎麼查空汙": "^(怎麼|如何)查(空汙|空氣|[Aa][Qq][Ii]|[Pp][Mm]2\.5)|查(空汙|空氣|[Aa][Qq][Ii]|[Pp][Mm]2\.5)教學$",
    # [功能設定]
    "目前狀態": "^(目前|查詢)狀態$",
    "說話模式調整": "^(不)?(可以|能|行|要|准)說別人教的話$",
    "聊天狀態調整": "^樹懶(醬)?(說話|講話|安靜|閉嘴)$"
}

#關鍵字正則（優先度：2）
regDict2 = {
    # [對答]
    "學說話": "^(樹懶(醬)?)?學說話$",
    "壞壞": "^(樹懶(醬)?)?壞壞$",
    # [爬蟲查詢]
    "商品查詢": "^(有(沒有)?賣)|((找|查(詢)?)?(商品|產品))|(有(沒有)?賣(嗎)?)$",
    "天氣查詢": "((查(詢)?)?天氣(怎樣|狀況|如何|查詢)?)|((會|有)下雨嗎)$",
    "空汙查詢": "(查(詢)?)?(空汙|空氣|[Aa][Qq][Ii]|[Pp][Mm]2\.5)(品質|怎樣|狀況|如何|查詢)?$",
    # [機率運勢]
    "擲筊": "(怎麼|如何|我要|樹懶(醬)?)?(擲筊|搏杯)|(擲筊|搏杯)教學$",
    "抽塔羅": "(怎麼|如何|我要|樹懶(醬)?)?抽塔羅(牌)?|(抽)?塔羅(牌)?教學$"
}

##關鍵字尋找（優先度：1）
def findReg1(msg):
    for keyword in regDict1.keys():
        # [教學/選單] 主選單、功能一覽、怎麼聊天、怎麼抽籤
        # 怎麼學說話、學過的話、怎麼抽籤式回答
        # 怎麼查氣象、怎麼查天氣、怎麼查空汙
        # [功能設定] 目前狀態、說話模式調整、聊天狀態調整
        if re.search(regDict1[keyword], msg): return keyword
    return ""

##關鍵字類型（優先度：2）
def findReg2(msg):
    for keyword in regDict2.keys():
        # [爬蟲查詢] 商品查詢
        if keyword=="商品查詢" and re.search(regDict2[keyword], msg): 
            KEY = re.split(regDict2[keyword], msg)[0].replace("嗎","")
            if not KEY: KEY = re.split(regDict2[keyword], msg)[::-1][0].replace("嗎","")
            return KEY + "商品查詢"

        # [爬蟲查詢] 天氣查詢
        elif keyword=="天氣查詢" and re.search(regDict2[keyword], msg):
            PATTERN = '((今|明|後|大後)[早晚天]|[一下]週|[早晚]上|中午|凌晨|清晨|未來|目前|現在|即時)'
            KEY = re.split(regDict2[keyword], msg)[0].replace("查詢", "")
            site = re.split(PATTERN, KEY.replace("台","臺"))
            if re.search(PATTERN, KEY.replace("台","臺")):
                if any(site[1] == s for s in ["今", "今天", "現在", "目前", "即時"]): return site[0] + "目前天氣"
                else: return site[0] + "未來天氣"
            else: return  site[0] + "目前天氣"
        
        # [爬蟲查詢] 空汙查詢
        elif keyword=="空汙查詢" and re.search(regDict2[keyword], msg): 
            KEY = re.split(regDict2[keyword], msg)[0].replace("查詢", "").replace("台","臺")
            return KEY + "空汙查詢"
        
        # [對答] 學說話、壞壞、指定暱稱、解除指定暱稱
        # [機率運勢] 擲筊、抽塔羅
        elif re.search(regDict2[keyword], msg): return keyword
    return ""

##關鍵字類型
def key(msg):
    result = findReg1(msg)
    return result if result else findReg2(msg)