with open("僅新聞詞庫.txt", 'r', encoding="UTF-8") as keyword_1:
    lines = keyword_1.readlines()
    a = set()
    for line in lines:     # 遍历数据
        # print(line)
        a.add(line.strip())

    print(len(a))
