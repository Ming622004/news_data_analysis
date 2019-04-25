import MySQLdb
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np
import sys

mongodb_db_name = "keyword"
mongodb_collection_name = "apple_news_test"
mongodb_ip = "127.0.0.1"

mariadb_db_name = "news_testdb"
mariadb_db_table = "test_news"

conn = MySQLdb.connect(host="127.0.0.1", user="root",passwd="mysql", db=mariadb_db_name, charset="utf8")
cursor = conn.cursor()

sql_command = "select create_time,tag,title_keyword_1,title_keyword_2,title_keyword_3,keyword_1,keyword_2,keyword_3," \
              "keyword_4,keyword_5,views_48 from " + mariadb_db_table + \
              " where views_48 is not null and create_time > '2019-02-07'"
cursor.execute(sql_command)
sql_data = cursor.fetchall()
cursor.close()
conn.close()

print(len(sql_data))

# 關鍵字24小時 48小時 72小時 趨勢 共32個x
title = []
keywordName = "tk"
for i in range(3):
    title.append(keywordName + str(i + 1) + "_24")
    title.append(keywordName + str(i + 1) + "_72")
    title.append(keywordName + str(i + 1) + "_168")
    title.append(keywordName + str(i + 1) + "_trend")
keywordName = "ck"
for i in range(5):
    title.append(keywordName + str(i + 1) + "_24")
    title.append(keywordName + str(i + 1) + "_72")
    title.append(keywordName + str(i + 1) + "_168")
    title.append(keywordName + str(i + 1) + "_trend")
title.append("48hr_views")

df_news = pd.DataFrame(columns=title)

conn_md = MongoClient(mongodb_ip)
mdb = conn_md[mongodb_db_name]
mcollection = mdb[mongodb_collection_name]

count = 0
for single_news in sql_data:
    count = count + 1
    if count % 200 == 0:
        print("已處理資料:", count)
    # 把時間拉出來
    newsCreateTime = single_news[0]
    # print(newsCreateTime)
    titleCount = 0
    dfData = {}
    for keywordPos in range(2, 10):
        # views = [[0],[0],[0],[0],[0],[0],[0]]
        views = [0,0,0,0,0,0,0]
        m_data = mcollection.find({"keyword": single_news[keywordPos]})[0]
        # print(m_data)
        for viewsCreateTimeStr in m_data["views"]:
            viewsCreateTime = datetime.strptime(viewsCreateTimeStr, "%Y-%m-%d %H:%M")
            dayDiff = (newsCreateTime- viewsCreateTime).total_seconds() // 86400
            dayDiff = int(dayDiff)
            if 0 <= dayDiff < 7:
                # print(viewsCreateTime, newsCreateTime, dayDiff, m_data["views"][viewsCreateTimeStr])
                views[dayDiff] = views[dayDiff] + int(m_data["views"][viewsCreateTimeStr])
        dfData[title[titleCount]] = views[0]
        titleCount = titleCount + 1
        dfData[title[titleCount]] = views[1] + views[2]
        titleCount = titleCount + 1
        dfData[title[titleCount]] = views[3] + views[4] + views[5] + views[6]
        titleCount = titleCount + 1
        # 計算斜率
        # model = LinearRegression(fit_intercept=True)
        lm = LinearRegression()
        # print(views)
        lm.fit(np.array([[0],[-1],[-2],[-3],[-4],[-5],[-6]]), np.array(views))
        # print(lm.intercept_)
        # print(lm.coef_)
        dfData[title[titleCount]] = lm.coef_
        titleCount = titleCount + 1

    dfData["48hr_views"] = single_news[-1]
    df_news = df_news.append(dfData, ignore_index=True)

print(df_news)

train_x = df_news.drop(["48hr_views"],axis=1)
train_y = df_news["48hr_views"]

lm.fit(train_x,train_y)
print(lm.intercept_)
print(lm.coef_)

predict = lm.predict(train_x)
print("r2 Score:",r2_score(train_y,predict))


