from pymongo import MongoClient
import MySQLdb, sys, datetime, time
import cb104_addr
import pandas as pd
import math

# 只針對比較高頻率的關鍵字
# "CT" "apple" "storm" "udn"
paper_name = "udn"

mongodb_db_host = cb104_addr.local_mongodb_host
mongodb_db_name = "keyword_filter"
mongodb_collection = paper_name + "_news"

conn_md = MongoClient(mongodb_db_host)
mdb = conn_md[mongodb_db_name]
mcollection = mdb[mongodb_collection]

ansTimeStart = datetime.datetime(2019, 2, 5, 0, 0)
endTime = datetime.datetime(2019, 3, 13, 0, 0)

count = 0
for keywordData in mcollection.find({}):
    count = count + 1
    if count % 100 == 0:
        print("處理資料:", count)
    viewsList = []
    keyDict = {}
    keywordName = keywordData["keyword"]
    keyDict["keywordName"] = keywordName
    keywordViews = keywordData["views"]
    time = ansTimeStart
    while (endTime - time).total_seconds() > 0:
        # .total_seconds()
        timeStr = datetime.datetime.strftime(time, "%Y-%m-%d %H:%M")
        if timeStr in keywordViews:
            viewsList.append(keywordViews[timeStr])
        else:
            viewsList.append(0)
        time = time + datetime.timedelta(hours=1)

    for i in range(24,len(viewsList)):
        time = ansTimeStart + datetime.timedelta(hours=24+i)
        timeStr = datetime.datetime.strftime(time, "%Y-%m-%d %H:%M")
        tmp_sum = sum(viewsList[i-24:i])
        if tmp_sum < 1:
            tmp_sum = 1
        keyDict[timeStr] = math.log10(tmp_sum)
    # print(keyDict)
    if count == 1:
        df = pd.DataFrame(keyDict, index=[0])
    else:
        df = df.append(keyDict, ignore_index=True)

print(df)
df.to_pickle("populationKeyword_" + paper_name + "_log.pkl")



