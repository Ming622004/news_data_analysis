import MySQLdb
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np
import sys
import cb104_addr

# "CT" "apple" "storm" "udn"
paper_name = "apple"

mongodb_db_host = cb104_addr.local_mongodb_host
mongodb_db_name = "keyword_filter"
mongodb_collection = paper_name + "_news"

mariadb_host = cb104_addr.local_mariadb_host
mariadb_user = cb104_addr.local_mariadb_user
mariadb_pw = cb104_addr.local_mariadb_pw
mariadb_db_name = "news_db"
mariadb_tablename = paper_name + "_news"

conn_md = MongoClient(mongodb_db_host)
mdb = conn_md[mongodb_db_name]
mcollection = mdb[mongodb_collection]

conn = MySQLdb.connect(host=mariadb_host, user=mariadb_user, passwd=mariadb_pw, db=mariadb_db_name, charset="utf8")
cursor = conn.cursor()

sql_command = "select create_time,tag,title_keyword_1,title_keyword_2,title_keyword_3,keyword_1,keyword_2,keyword_3," \
              "keyword_4,keyword_5,views_48 from " + mariadb_tablename + \
              " where views_48 is not null and create_time > '2019-02-07'"
cursor.execute(sql_command)
sql_data = cursor.fetchall()
cursor.close()
conn.close()

print(len(sql_data))


def take_second(elem):
    return elem[1]


# 讀取keyword資料
keywordDict = {}
count1 = 0
with open("new_keyword0317.txt","r",encoding="utf-8") as kwh:
    data = kwh.read()
    data_line = data.split("\n")
    kwSet = set()
    for i in range(1, len(data_line)-1):
        # print("data",data_line[i])
        a = eval(data_line[i])

        if a[0].strip().upper() not in keywordDict:
            keywordDict[a[0].strip().upper()] = a[1]
        else:
            keywordDict[a[0].strip().upper()] = keywordDict[a[0].strip().upper()] + a[1]
delList = []
for keyword in keywordDict:
    if keywordDict[keyword] < 100:
        delList.append(keyword)

for keyword in delList:
    del keywordDict[keyword]

for i in range(10,21):
    if str(i) in keywordDict:
        del keywordDict[str(i)]
title = ["k1_24", "k1_48", "k1_168", "k1_trend",
         "k2_24", "k2_48", "k2_168", "k2_trend",
         "k3_24", "k3_48", "k3_168", "k3_trend", "48hr_views"]
df_news = pd.DataFrame(columns=title)

count_data = 0
for sqlDataOneRow in sql_data:
    newsCreateTime = sqlDataOneRow[0]
    # print(newsCreateTime)
    titleCount = 0
    dfData = {}
    keywordData = set()
    # 這邊要判斷有沒有進重要字
    for keywordPos in range(2, 10):
        if sqlDataOneRow[keywordPos] is not None:
            keywordData.add(sqlDataOneRow[keywordPos].strip().upper())

    sqlKeywordList = []
    for keyword in keywordData:
        if keyword in keywordDict:
            sqlKeywordList.append([keyword, keywordDict[keyword]])

    if len(sqlKeywordList) >= 3:
        count1 = count1 + 1
        sqlKeywordList.sort(key=take_second, reverse=True)
        # print(sqlKeywordList)
    else:
        continue
    count_data = count_data + 1
    if count_data % 500 == 0:
        print("已處理資料:",count_data)
    keyName = ["k1", "k2", "k3"]
    try:
        for keywordPos in range(3):
            # views = [[0],[0],[0],[0],[0],[0],[0]]
            views = [0,0,0,0,0,0,0]
            m_data = mcollection.find({"keyword": sqlKeywordList[keywordPos][0]})[0]
            # print(m_data)
            for viewsCreateTimeStr in m_data["views"]:
                viewsCreateTime = datetime.strptime(viewsCreateTimeStr, "%Y-%m-%d %H:%M")
                dayDiff = (newsCreateTime - viewsCreateTime).total_seconds() // 86400
                dayDiff = int(dayDiff)
                if 0 <= dayDiff < 7:
                    # print(viewsCreateTime, newsCreateTime, dayDiff, m_data["views"][viewsCreateTimeStr])
                    views[dayDiff] = views[dayDiff] + int(m_data["views"][viewsCreateTimeStr])
                dfData[keyName[keywordPos]+"_24"] = views[0]
                dfData[keyName[keywordPos]+"_48"] = views[1] + views[2]
                dfData[keyName[keywordPos]+"_168"] = views[3] + views[4] + views[5] + views[6]
                # 計算斜率
                # model = LinearRegression(fit_intercept=True)
                lm = LinearRegression()
                # print(views)
                lm.fit(np.array([[0], [-1], [-2], [-3], [-4], [-5], [-6]]), np.array(views))
                # print(lm.intercept_)
                # print(lm.coef_)
                dfData[keyName[keywordPos] + "_trend"] = lm.coef_
        dfData["48hr_views"] = sqlDataOneRow[-1]
        df_news = df_news.append(dfData, ignore_index=True)
    except Exception as e:
        print(sqlKeywordList)
        print(e)


# ===================================

train_x = df_news.drop(["48hr_views"],axis=1)
train_y = df_news["48hr_views"]

lm.fit(train_x, train_y)
print(lm.intercept_)
print(lm.coef_)

predict = lm.predict(train_x)
print("r2 Score:", r2_score(train_y, predict))


