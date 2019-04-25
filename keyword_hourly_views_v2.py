from pymongo import MongoClient
import MySQLdb, sys, datetime, queue, threading, time
import cb104_addr
# db.apple_news.createIndex( { "keyword": 1 }, { unique: true } )

mongodb_db_name = "keyword"
mongodb_collection_name = "apple_news"
mongodb_ip = "127.0.0.1"

mariadb_db_name = "news_testdb"
mariadb_db_table = "test_news"

papername = "apple"

conn = MySQLdb.connect(host="127.0.0.1", user="root",passwd="mysql", db=mariadb_db_name, charset="utf8")
cursor = conn.cursor()

# 把sql資料庫資料撈出來
sql_command = "select * from " + mariadb_db_table
cursor.execute(sql_command)
sql_data = cursor.fetchall()
cursor.close()
conn.close()

print("資料總筆數:", len(sql_data))

sql_news_data = queue.Queue()


# 計算出在兩個整點間的觀看數
# 重要! 資料量會少 原本可能最後四小時有資料 變成只有最後兩個小時有資料
def view_on_hour(minute_pos, views):
    hourly_news_view = []  # 在整點這篇新聞的觀看數
    views_in_hour = []
    view_finalvalue_pos = 0

    # 先插出整點的觀看數hourly_news_view
    views.insert(0, 0)
    for hour in range(1,len(views)):
        if views[hour] is not None and views[hour-1] is not None:
            hourly_news_view.append(views[hour] - (views[hour]-views[hour-1])*minute_pos/60)
        else:
            hourly_news_view.append(None)

    # 算出整點間差距
    hourly_news_view.insert(0, 0)
    for hour in range(1, len(hourly_news_view)):
        if hourly_news_view[hour] is not None and hourly_news_view[hour - 1] is not None:
            view_finalvalue_pos = hour
            views_in_hour.append(int(hourly_news_view[hour]-hourly_news_view[hour-1]))
        else:
            views_in_hour.append(None)

    # print(view_on_hour)
    return view_finalvalue_pos, views_in_hour


def data_into_mongodb(sql_news_data):
    count = 0
    keyword_position = ["ck1", "ck2", "ck3", "ck4", "ck5", "ck6", "ck7", "ck8", "ck9", "ck10", "tk1", "tk2", "tk3"]
    conn_md = MongoClient(mongodb_ip)
    mdb = conn_md[mongodb_db_name]
    mcollection = mdb[mongodb_collection_name]
    while True:
        try:
            # 不阻塞的讀取佇列資料
            sql_data_onerow = sql_news_data.get_nowait()
            count = count + 1
            if count % 100 == 0:
                print(threading.currentThread().name, "已處理資料: ",count)
            # i = sql_news_data.qsize()
        except Exception as e:
            break

        keyword_word = list(sql_data_onerow[7:17] + sql_data_onerow[3:6])
        # print(keyword_word)
        views_data = list(sql_data_onerow[27:])

        # 判斷最後一個有觀看數的位置
        # print("分鐘數:", sql_data_onerow[1].minute)
        test_timed = 60 - sql_data_onerow[1].minute
        time1 = sql_data_onerow[1] + datetime.timedelta(minutes=test_timed)
        # print("整點時間", time1.strftime("%Y-%m-%d %H:%M"))
        # 判斷最後一個有觀看數的位置:count_view_value_pos  整點間觀看數:hourly_view
        count_view_value_pos, hourly_view = view_on_hour(sql_data_onerow[1].minute, views_data)
        # print(count_view_value_pos)
        # 如果都是None 先pass
        # 因為網址有.當mongoDB的key會有問題 所以把.先取代成__
        news_url = sql_data_onerow[0].replace(".", "__")

        for news_keyword1 in keyword_word:

            m_data = mcollection.find({"keyword": news_keyword1})

            try:
                # 如果找不到這個keyword 先把這個keyword insert 否則之後取key會有錯 並重新把這個檔案設定成變數m_data
                if m_data.count() == 0:
                    mcollection.insert({"keyword": news_keyword1, "url_done": [],"url_apply": [], "source": {}, "views": {}})
                    # 重新設定m_data 讓資料可以被key可以被讀到
                    m_data = mcollection.find({"keyword": news_keyword1})
                # 超過2筆代表忘了設定成唯一 資料庫之前就被另外的方始處理過造成問題
                # ==============發生的話讓程式停止================
                elif m_data.count() > 1:
                    print("===warning: 'keyword' should be unique in mongoDB===")
                    print("keyword'"+news_keyword1+"' is duplicate")
            except Exception as e:
                print(e)

            # 判斷url位置
            # 如果此url已經被放進去done
            if news_url in m_data[0]["url_done"]:
                continue
            # 如果在處理區
            elif news_url in m_data[0]["url_apply"]:
                # 判斷baffle是不是比新的值小 是的話執行 並更新baffle
                # print(m_data[0])
                if count_view_value_pos > m_data[0]["source"][news_url]["baffle"]:

                    # 把view加進某個時間點
                    push_hourly_view = {}
                    for hour in range(m_data[0]["source"][news_url]["baffle"], count_view_value_pos):
                        if hourly_view[hour] is not None:
                            view_time = time1 + datetime.timedelta(hours=hour)
                            push_hourly_view["views." + view_time.strftime("%Y-%m-%d %H:%M")] = hourly_view[hour]
                    if len(push_hourly_view) is not 0:
                        mcollection.update({"keyword": news_keyword1}, {"$inc": push_hourly_view})

                    # 如果是第72小時 移動到done 檢查關鍵字
                    if count_view_value_pos == 72:
                        mcollection.update({"keyword": news_keyword1},
                                           {"$pull": {"url_apply": news_url}})
                        mcollection.update({"keyword": news_keyword1},
                                           {"$push": {"url_done": news_url}})
                # 小於等於baffle就不管 !!之後要加時間超過多少就移到done
                else:
                    continue

            # 此網址第一次出現在這個關鍵字
            else:
                keyword_index = [keyword_position[pos] for pos, word in enumerate(keyword_word) if word == news_keyword1]
                # print(keyword_index)
                mcollection.update({"keyword": news_keyword1},
                                   {"$set": {"source." + news_url: {"keyword_index": keyword_index,
                                                                    "baffle": count_view_value_pos}}})
                # 條件符合移動到 apply 不符合移動到 done
                if count_view_value_pos == 72:
                    mcollection.update({"keyword": news_keyword1},
                                       {"$push": {"url_done": news_url}})
                else:
                    mcollection.update({"keyword": news_keyword1},
                                       {"$push": {"url_apply": news_url}})

                push_hourly_view = {}
                for hour in range(0, count_view_value_pos):
                    if hourly_view[hour] is not None:
                        view_time = time1 + datetime.timedelta(hours=hour)
                        push_hourly_view["views." + view_time.strftime("%Y-%m-%d %H:%M")] = hourly_view[hour]
                if len(push_hourly_view) is not 0:
                    mcollection.update({"keyword": news_keyword1}, {"$inc": push_hourly_view})


if __name__ == "__main__":
    # content keyword & title keyword 給個名字
    start_time = time.time()
    for sql_data_row in sql_data:
        sql_news_data.put(sql_data_row)

    threads = []
    # 可以調節執行緒數，進而控制抓取速度
    threadNum = 10
    for i in range(0, threadNum):
        t = threading.Thread(target=data_into_mongodb, args=(sql_news_data,))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        # 多執行緒多join的情況下，依次執行各執行緒的join方法，這樣可以確保主執行緒最後退出，且各個執行緒間沒有阻塞
        t.join()

    end_time = time.time()
    timeCost = end_time - start_time
    print(timeCost)

