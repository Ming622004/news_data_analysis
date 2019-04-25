import MySQLdb, sys, datetime, time
import cb104_addr
import numpy as np

# 只針對比較高頻率的關鍵字
# "CT" "apple" "storm" "udn"
paper_name = "apple"

mariadb_host = cb104_addr.local_mariadb_host
mariadb_user = cb104_addr.local_mariadb_user
mariadb_pw = cb104_addr.local_mariadb_pw
mariadb_db_name = "news_db"
mariadb_tablename = paper_name + "_news"

conn = MySQLdb.connect(host=mariadb_host, user=mariadb_user, passwd=mariadb_pw, db=mariadb_db_name, charset="utf8")
cursor = conn.cursor()

sql_command = "select create_time,tag,title_keyword_1,title_keyword_2,title_keyword_3,keyword_1,keyword_2,keyword_3," \
              "keyword_4,keyword_5,views_48 from " + mariadb_tablename + \
              " where views_48 is not null and create_time > '2019-02-07' and (title_keyword_1 = '韓國瑜'" \
              " or title_keyword_2 = '韓國瑜' or title_keyword_3 = '韓國瑜' or keyword_1 = '韓國瑜' " \
              "or keyword_2 = '韓國瑜' or keyword_3 = '韓國瑜' or keyword_4 = '韓國瑜' or keyword_5 = '韓國瑜')" \
              " order by views_48"
cursor.execute(sql_command)
sql_data = cursor.fetchall()
cursor.close()
conn.close()

a = []
for i in sql_data:
    print(i)
    a.append(int(i[-1]))

a = np.array(a)
print("mean", np.mean(a))
print("max", np.max(a))
print("min", np.min(a))
print("std", np.std(a))
print("median", np.median(a))
