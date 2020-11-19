#!/usr/bin/python3
# coding: utf-8

import pymongo
import re

# 耗时评论的模式 yyyymmdd (h) comentsMsg
reg = r"\d*\s\(.*\)"

# mongodb
dbClient = pymongo.MongoClient("mongodb://192.168.50.50:27018/")
dbWekan = dbClient["wekan"]
cardsDoc = dbWekan["cards"]

# 查询耗时为0的卡片
query = {"startAt": {"$exists": True}}

resultRows = cardsDoc.find(query)

for x in resultRows:
    # 初始化每个卡片的耗时
    time = 0
    
    cardID = x["_id"]
    cardCommentsDoc = dbWekan["card_comments"]
    # 查询已经开始且有评论的卡片
    query = {"cardId": cardID}
    cardCommentsRows = cardCommentsDoc.find(query)
    
    for y in cardCommentsRows:
        # 匹配耗时评论并计算总计时间
        timeReg = re.search(reg, y["text"])
        if timeReg:
            time += float(timeReg.group().split("(")[-1].split(")")[0])
    # 计算结果写入数据库
    if time != 0:
        query = {"_id": cardID}
        spentTimeValues = {"$set": {"spentTime": time}}
        cardsDoc.update_one(query, spentTimeValues)
    elif "endAt" in x:
        dTime = x["endAt"] - x["startAt"]
        time = round(dTime.total_seconds()/60/60, 1)
        query = {"_id": cardID}
        spentTimeValues = {"$set": {"spentTime": time}}
        cardsDoc.update_one(query, spentTimeValues)

