# 用法：from md转html import md2html（或 python3 -I md转html.py 输入.md）
# 只支持档案用到的写法：标题、表格、无序与有序列表、段落、加粗、行内代码
import html
import re
import sys


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    # 数字与单位之间不换行
    s = re.sub(r"(?<=[0-9]) (?=(个|项|张|秒|款|天|次|档|万|笔|级|名|倍|元|小时|分钟|人|日|%))", "&nbsp;", s)
    return s


def md2html(text, top=2):
    out, i = [], 0
    lines = text.split("\n")
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", l)
        if m:
            lv = {1: 3, 2: 3, 3: 4, 4: 5}.get(len(m.group(1)), 6)
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue
        if l.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            body = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c or "--") for c in r)]
            t = ["<table>"]
            for k, r in enumerate(body):
                tag = "th" if k == 0 else "td"
                t.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", l):
            ordered = bool(re.match(r"^\s*\d+\.", l))
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                    items[-1] += " " + lines[i].strip()
                    i += 1
            tag = "ol" if ordered else "ul"
            out.append(f'<{tag} class="pl">' + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if l.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre>" + "\n".join(buf) + "</pre>")
            continue
        para = [l.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*([-*]|\d+\.)\s|```)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


if __name__ == "__main__":
    print(md2html(open(sys.argv[1], encoding="utf-8").read()))
