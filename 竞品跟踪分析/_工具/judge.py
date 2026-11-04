# 用法：
#   python3 -I judge.py 覆盖            检查每张关键帧在观察记录里都有帧号（清1）
#   python3 -I judge.py 报告 <报告.html>  检查图片与帧号引用都存在（清3），列出带逗号的句子（清8）
import html as H
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KF = os.path.join(ROOT, "素材", "关键帧")
OBS = os.path.join(ROOT, "过程")
REF = re.compile(r"录屏([123])\s*t(\d{4}\.\d)")


def keyframes(n):
    d = os.path.join(KF, f"录屏{n}")
    return sorted(f[1:-4] for f in os.listdir(d) if f.endswith(".jpg"))


def coverage():
    bad = 0
    for n in (1, 2, 3):
        p = os.path.join(OBS, f"观察记录_录屏{n}.md")
        if not os.path.exists(p):
            print(f"✘ 录屏{n}：没有观察记录")
            bad += 1
            continue
        text = open(p, encoding="utf-8").read()
        # 允许「录屏2 t0003.5、t0005.5」这种并列写法：收集文中所有 t 数字
        seen = set(re.findall(r"t(\d{4}\.\d)", text))
        miss = [k for k in keyframes(n) if k not in seen]
        print(("✔" if not miss else "✘") + f" 录屏{n}：关键帧 {len(keyframes(n))} 张，未记录 {len(miss)} 张" + (f"：{' '.join(miss)}" if miss else ""))
        bad += bool(miss)
    return bad


def report(path):
    src = open(path, encoding="utf-8").read()
    base = os.path.dirname(os.path.abspath(path))
    bad = 0
    nos = re.sub(r"<script[^>]*>.*?</script>", "", src, flags=re.S)
    imgs = re.findall(r"<img[^>]+src=\"([^\"]+)\"", nos)
    for s in imgs:
        if s.startswith("data:"):
            continue
        if not os.path.exists(os.path.join(base, H.unescape(s))):
            print(f"✘ 图片不存在：{s}")
            bad += 1
    print(f"图片引用 {len(imgs)} 处，缺失 {bad} 处")
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", src, flags=re.S)
    text = H.unescape(re.sub(r"<[^>]+>", "\n", body))
    refs = set(REF.findall(text))
    miss = [f"录屏{n} t{t}" for n, t in sorted(refs)
            if not os.path.exists(os.path.join(KF, f"录屏{n}", f"t{t}.jpg"))
            and not os.path.exists(os.path.join(ROOT, "素材", "每秒帧", f"录屏{n}", f"t{t}.jpg"))]
    print(f"帧号引用 {len(refs)} 个，找不到 {len(miss)} 个" + (f"：{'、'.join(miss)}" if miss else ""))
    bad += len(miss)
    print("\n带逗号的句子（逐句判断逗号两边有没有关系）：")
    k = 0
    for line in text.split("\n"):
        line = line.strip()
        for sent in re.split(r"(?<=[。！？；])", line):
            if "，" in sent:
                k += 1
                print(f"  {k}. {sent}")
    return bad


if __name__ == "__main__":
    if sys.argv[1] == "覆盖":
        sys.exit(1 if coverage() else 0)
    if sys.argv[1] == "报告":
        sys.exit(1 if report(sys.argv[2]) else 0)
