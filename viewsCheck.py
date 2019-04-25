import MySQLdb, sys, datetime, time
import cb104_addr

# 只針對比較高頻率的關鍵字
# "CT" "apple" "storm" "udn"
paper_name = "CT"

mariadb_host = cb104_addr.local_mariadb_host
mariadb_user = cb104_addr.local_mariadb_user
mariadb_pw = cb104_addr.local_mariadb_pw
mariadb_db_name = "news_db"
mariadb_tablename = paper_name + "_news"

conn = MySQLdb.connect(host=mariadb_host, user=mariadb_user, passwd=mariadb_pw, db=mariadb_db_name, charset="utf8")
cursor = conn.cursor()

sql_command = "select * from " + mariadb_tablename
cursor.execute(sql_command)
sql_data = cursor.fetchall()
cursor.close()
conn.close()
ansTimeStart = datetime.datetime(2019, 2, 5, 0, 0)
# print(ansTimeStart)

def view_on_hour(minite_pos, views):
    hourly_news_view = []  # 在整點這篇新聞的觀看數
    views_in_hour = []
    view_finalvalue_pos = 0

    # 先插出整點的觀看數hourly_news_view
    views.insert(0, 0)
    for hour in range(1,len(views)):
        if views[hour] is not None and views[hour-1] is not None:
            if views[hour] < 0 or views[hour-1] < 0:
                print("error:", views[hour],views[hour-1])
            hourly_news_view.append(views[hour] - (views[hour]-views[hour-1])*minite_pos/60)
        else:
            hourly_news_view.append(None)

    # 算出整點間差距
    hourly_news_view.insert(0, 0)
    for hour in range(1, len(hourly_news_view)):
        if hourly_news_view[hour] is not None and hourly_news_view[hour - 1] is not None:
            view_finalvalue_pos = hour
            temp_view = int(hourly_news_view[hour]-hourly_news_view[hour-1])
            if temp_view < 0:
                temp_view = 0
            views_in_hour.append(temp_view)
        else:
            views_in_hour.append(None)

    # print(view_on_hour)
    return view_finalvalue_pos, views_in_hour


hourlyViews = {}
for sqlDataOneRow in sql_data:
    views_data = list(sqlDataOneRow[27:])
    test_timed = 60 - sqlDataOneRow[1].minute
    time1 = sqlDataOneRow[1] + datetime.timedelta(minutes=test_timed)
    # print("整點時間", time1.strftime("%Y-%m-%d %H:%M"))
    # 判斷最後一個有觀看數的位置:count_view_value_pos  整點間觀看數:hourly_view
    count_view_value_pos, hourly_view = view_on_hour(sqlDataOneRow[1].minute, views_data)
    # print(count_view_value_pos)
    # 如果都是None 先pass
    for hour2 in range(0, count_view_value_pos):
        view_time = (time1 + datetime.timedelta(hours=hour2)).strftime("%Y-%m-%d %H:%M")
        if hourly_view[hour2] is None:
            continue
        # elif hourly_view[hour2] < 0:
        #     print("error", hourly_view)
        #     print(sqlDataOneRow)
        #     print(test_timed, time1)
        #     break
        elif view_time in hourlyViews:
            hourlyViews[view_time] = hourlyViews[view_time] + hourly_view[hour2]
        else:
            hourlyViews[view_time] = hourly_view[hour2]

dayDiff = [0] * 24
for hour3 in range(865):
    view_time = (ansTimeStart + datetime.timedelta(hours=hour3)).strftime("%Y-%m-%d %H:%M")
    if view_time in hourlyViews:
        print(hourlyViews[view_time])
        dayDiff[hour3 % 24] = dayDiff[hour3 % 24] + hourlyViews[view_time]
    else:
        print(0)

print(dayDiff)

