##########抽籤功能##########
import os, sys, json, math, random

## 擲筊
def getDevinate():
    num = int(random.random()*4)
    img = ['divinationblocks/00.png', 'divinationblocks/01.png', 'divinationblocks/01.png', 'divinationblocks/11.png']
    res = ['笑筊', '聖筊', '聖筊', '陰筊']
    return {"url": img[num], "text": res[num]}

## 抽塔羅牌
def getTarot(num):
    #正逆位隨機
    pList = list(range(100))
    random.shuffle(pList)
    #正逆位綁卡片上
    cardList = list(range(100))
    cardList = list(zip(pList[:78], cardList))
    #卡片洗牌
    random.shuffle(cardList)
    #讀入卡片資料
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tarot_info.json'), 'r', encoding="UTF-8") as json_file:
        TAROT = json.load(json_file)
        #取牌
        result = []
        for i in range(num):
            position_delta = cardList[i][0]%2
            cardId = cardList[i][1] * 2 + position_delta
            #取牌
            card = TAROT[str(cardId)]
            card['id'] = str(cardId)
            result.append(card)
        return result

## 取得塔羅牌義
def getMeaningTarot(id):
    #讀入卡片資料
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tarot_info.json'), 'r', encoding="UTF-8") as json_file:
        TAROT = json.load(json_file)
        return TAROT[str(id)]
