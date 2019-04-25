import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates

keyword = "柯文哲"
hourInterval = 3

df_apple = pd.read_pickle(".\data\populationKeyword_apple.pkl")
df_udn = pd.read_pickle(".\data\populationKeyword_udn.pkl")
df_CT = pd.read_pickle(".\data\populationKeyword_CT.pkl")

# df_apple = pd.read_pickle("populationKeyword_apple_log.pkl")
# df_udn = pd.read_pickle("populationKeyword_udn_log.pkl")
# df_CT = pd.read_pickle("populationKeyword_CT_log.pkl")

df_apple = df_apple.fillna(0)
df_udn = df_udn.fillna(0)
df_CT = df_CT.fillna(0)

#print(df)
hourlyViews = []
hourlyViews.append(df_apple[df_apple["keywordName"] == keyword].drop("keywordName", axis=1).values.tolist()[0])
hourlyViews.append(df_udn[df_udn["keywordName"] == keyword].drop("keywordName", axis=1).values.tolist()[0])
hourlyViews.append(df_CT[df_CT["keywordName"] == keyword].drop("keywordName", axis=1).values.tolist()[0])

output = []
for i in range(3):
    tmp = []
    for j in range(168, len(hourlyViews[i]), hourInterval):
        mean = np.mean(hourlyViews[i][j - 168: j])
        # j - 120
        std = np.std(hourlyViews[i][j - 168: j])
        if std < 1:
            std = 10000
            tmp.append(0)
        else:
            tmp.append((hourlyViews[i][j]-mean)/std)
    output.append(tmp)

x = np.arange(0,len(output[0]))
x_time = []
ansTimeStart = datetime.datetime(2019, 2, 5, 0, 0)
for i in range(168, len(hourlyViews[i]), hourInterval):
    time = ansTimeStart + datetime.timedelta(hours=i)
    x_time.append(time)
    # if time.hour == 0 and time.day % 5 == 0:
    #     x_time.append(datetime.datetime.strftime(time, "%m-%d"))
    # else:
    #     x_time.append("")

print(output[0])
print(output[1])
print(output[2])
print(x_time)
# x_time = pd.to_datetime(x_time)

plt.figure(figsize=(12, 4))

plt.plot(x_time, output[0], label='apple')
plt.plot(x_time, output[1], label='udn')
plt.plot(x_time, output[2], label='chinatimes')

# 設定圖的範圍, 不設的話，系統會自行決定
# plt.xlim(0, len(output[0]))
# plt.xlim(ansTimeStart+datetime.timedelta(day=7),ansTimeStart+datetime.timedelta(day=37))
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  #設置x軸主刻度顯示格式（日期）
# plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=14))
plt.ylim(-6, 6)
plt.legend()

plt.xlabel("time")
plt.ylabel("Popularity std")

# 在這個指令之前，都還在做畫圖的動作
# 這個指令算是 "秀圖"
plt.show()


