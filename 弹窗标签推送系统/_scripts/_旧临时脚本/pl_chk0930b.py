import re, openpyxl
B = "/Users/decheng.huang/claude/弹窗标签推送系统/"
def txt(p):
    with open(B + p, encoding="utf-8") as f:
        return f.read()
def grep(p, terms, w=70):
    s = txt(p)
    s2 = re.sub(r"<[^>]+>", "", s) if p.endswith(".html") else s
    for t in terms:
        idx = [m.start() for m in re.finditer(re.escape(t), s2)]
        print(f"--[{p}] {t}: {len(idx)}")
        for i in idx[:6]:
            print("    …" + s2[max(0, i - w):i + w].replace("\n", " ⏎ ") + "…")
grep("决策汇报.html", ["只有 2 项", "推送条", "按 A29 重核", "停用", "『或』已上线", "有条件才建的 5", "依据：2 项", "可以原样转发", "先别转发", "审查核对通过后转发"])
grep("支撑文件/04_弹窗功能缺口需求.md", ["只能做切换前后对比"])
grep("支撑文件/05_标签需求.md", ["已绑定触达渠道"])
grep("分析/A32_问题空间扫描.md", ["押注相同", "+4.14"])
grep("支撑文件/02_弹窗分人群定制方案.html", ["金卡以上且储值未下滑", "非金卡以上"])
grep("环节3_方案.html", ["申请过闸", "退出主线", "首期停用", "只有 2 项", "推送条"])
wb = openpyxl.load_workbook(B + "支撑文件/03_弹窗配置单.xlsx", data_only=True)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if isinstance(v, str) and ("第一批" in v or "第 0 步" in v or "不依赖外部答复" in v):
                print(ws.title, c.coordinate, v[:300].replace("\n", " ⏎ "))
