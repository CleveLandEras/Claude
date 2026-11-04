import re
P = "/Users/decheng.huang/claude/弹窗标签推送系统/"
keys = ["ID10", "ID11", "开放期", "潜在流失", "首储礼包"]
for f in ["02_弹窗分人群定制方案_迭代稿.html"]:
    txt = open(P + f, encoding="utf-8").read()
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt)
    for k in keys:
        for m in re.finditer(k, txt):
            print(f"[{k}]", txt[max(0, m.start() - 90): m.end() + 110])
        print("----")
