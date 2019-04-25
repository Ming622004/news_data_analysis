import pandas as pd
import MySQLdb
import cb104_addr

paper_name = "apple"

mariadb_host = cb104_addr.local_mariadb_host
mariadb_user = cb104_addr.local_mariadb_user
mariadb_pw = cb104_addr.local_mariadb_pw
mariadb_db_name = "news_db"
mariadb_tablename = paper_name + "_news"

conn = MySQLdb.connect(host=mariadb_host, user=mariadb_user, passwd=mariadb_pw, db=mariadb_db_name, charset="utf8")
cursor = conn.cursor()

# sql_command = "select * from " + mariadb_tablename

sql_command = sql_command = "select create_time,tag,title_keyword_1,title_keyword_2,title_keyword_3," \
                            "keyword_1,keyword_2,keyword_3,keyword_4,keyword_5,views_48 from " + mariadb_tablename + \
                            " where views_48 is not null and create_time > '2019-02-10'"

# cursor.execute(sql_command)
# sql_data = cursor.fetchall()

df = pd.read_sql(sql_command, conn)
# df.columns = sql_data.keys()

cursor.close()
conn.close()
print(df)
print(df.columns)

