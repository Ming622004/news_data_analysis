import pandas as pd
import MySQLdb

a = [0]
a = a * 24
a[23] = 15
print(a)


# df = pd.DataFrame(columns=['A', 'B'])
# for i in range(5):
#     df = df.append({'A': i, 'B': i}, ignore_index=True)
# print(df)
#
# mariadb_db_name = "news_testdb"
# mariadb_db_table = "test_news"
#
# conn = MySQLdb.connect(host="127.0.0.1", user="root",passwd="mysql", db=mariadb_db_name, charset="utf8")
# cursor = conn.cursor()
#
# sql_command = "select * from " + mariadb_db_table + " where create_time > 2019-02-07"
# cursor.execute(sql_command)
# sql_data = cursor.fetchall()
# cursor.close()
# conn.close()
#
# print(len(sql_data))
# print(type(sql_data[0][1]))