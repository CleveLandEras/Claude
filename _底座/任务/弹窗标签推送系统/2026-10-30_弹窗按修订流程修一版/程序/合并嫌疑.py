#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并嫌疑.py  把本夹六张嫌疑清单（a、b、c、d1、d2、e）合成 本夹/嫌疑总表.md

读什么：本夹 嫌疑_a_*.md、嫌疑_b_*.md、嫌疑_c_*.md、嫌疑_d1_*.md、嫌疑_d2_*.md、嫌疑_e_*.md（缺哪张跳过哪张，出来后重跑即可）。
每张清单一行一条：编号｜嫌疑（或问题）｜出处｜严重度｜去向。

链编号怎么定（同编号归一组）：
  b、c：出处开头的〔…〕里的第一个编号（追链编号，如 B1-F03）。
  d1、d2：①出处和正文里「」引号中的控件可见文字 → 查控件回指表「控件」列 → 该控件的字段编号（出处里写了页名的，只留该页的控件）；
         ②出处里「框架 L227」「框架 L349–360」之类行号 → 追链.py 算出的字段框架行；③仍没有的，用字段名（去括号、长度 ≥4）在正文里找。三路按命中次数计票，取票多的字段／入口编号。
  a、e：只走③（和 ②）。没找到的写「—」，每条自成一组，不归并。
已在待拍板第 N 件：待查 4 的关键词（原夹 里程碑1_底稿/待拍板汇总.md 的 10 件＋原任务交付「要你定」的 1 件＝第 11 件）。
  每件有强词（命中一个就算）和弱词（要命中两个），写在 TUOPAIBAN。命中是文字匹配，写出命中的词，第二级核对后再填去向。
已在研发待确认第 N 条：研发评审待确认.md 的第 N 条，同样强词／弱词（YANFA）。只配弹窗相关的 1–8、18–21、23–28。
保留：嫌疑总表.md 里已填的「去向」「内容定性」按编号带回（重跑不丢）；来源清单里已填的去向也带入。
输出列：编号｜来源｜链编号｜嫌疑｜严重度｜已在待拍板或研发待确认｜去向（空）｜内容定性（空）
最后打印「去向为空 N 条」。
用法：python3 合并嫌疑.py
"""
import re, sys, importlib.util
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
BEN = HERE.parent
spec = importlib.util.spec_from_file_location('zl', HERE / '追链.py')
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)

SRC_GLOB = [('a', '嫌疑_a_*.md'), ('b', '嫌疑_b_*.md'), ('c', '嫌疑_c_*.md'), ('d1', '嫌疑_d1_*.md'), ('d2', '嫌疑_d2_*.md'), ('e', '嫌疑_e_*.md')]
OUT = BEN / '嫌疑总表.md'
SEV = {'高': 0, '中': 1, '低': 2}

# 待拍板 11 件：(强词, 弱词) —— 第 1–10 件来自 待拍板汇总.md，第 11 件来自原任务交付「要你定」
TUOPAIBAN = {
    1: ('去掉〔旧〕弹窗类型后；活动几个＋礼包 1 个；固定的每次弹几个', ['弹窗类型', '每次最多弹几个', '固定的', '占满', '活动类', '储值类']),
    2: ('每人每天最多弹几个 默认 8 个', ['默认 8', '每人每天最多弹几个', '16 个', '8 个']),
    3: ('弹出间隔 默认 30 分钟', ['默认 30 分钟', '弹出间隔', '30 分钟', '场景间隔']),
    4: ('弹出时机 6 项减到 4 项、改单选', ['当天第 2 次登录', '当天第 N 次登录', '弹出时机', '多选', '单选']),
    5: ('不再默认排除 VIP 名单', ['VIP', '默认排除', '排除群组']),
    6: ('次数只做每人每天几次，不做每人总共几次', ['每人总共几次', '生涯一次', '总共几次', '每人每天几次']),
    7: ('点击后是否跳转默认是；弹出时机按类型给默认', ['点击后是否跳转', '默认：是', '默认「是」', '按类型给默认']),
    8: ('去掉〔旧〕标签状态开关', ['标签状态', '启用开关']),
    9: ('改场景设置不再推算人数', ['下次进入会变的人数', '多拦或少拦', '保存前预估', '推算']),
    10: ('规则名称只留一个，不分三语', ['繁中', '越南文', '三种语言', '三份', '名称']),
    11: ('查某个人过去（昨天）为什么没弹，本期做不做', ['昨天为什么没弹', '过去为什么没弹', '前几天', '历史弹出', '收到记录', '为什么没弹']),
}
# 强词：命中一个就算；弱词：命中两个才算。下面第一项只是说明，强词在 STRONG 里。
STRONG = {
    1: ['弹窗类型', '固定的每次弹几个', '活动几个'],
    2: ['默认 8', '默认 8 个'],
    3: ['默认 30 分钟', '场景间隔'],
    4: ['当天第 2 次登录', '当天第 N 次登录', '6 项减到 4 项'],
    5: ['VIP 名单', '默认排除'],
    6: ['每人总共几次', '生涯一次', '总共几次'],
    7: ['按类型给默认'],
    8: ['标签状态', '启用开关'],
    9: ['下次进入会变的人数', '多拦或少拦', '保存前预估'],
    10: ['越南文', '三种语言', '三份'],
    11: ['昨天为什么没弹', '过去为什么没弹', '前几天为什么没弹'],
}
# 研发评审待确认：条号 → (强词, 弱词)
YANFA = {
    1: (['单笔', '单局', '本次登录累计', '押注金额按'], ['买了指定礼包后', '押注达到指定金额', '场景参数']),
    2: (['一次登录', '断线重连', '杀进程', '换设备'], ['跨天', '跨 0 点', '重连']),
    3: (['登录后进入大厅', '区分登录后'], ['从游戏返回', '客户端能否区分', '登录后进入']),
    4: (['权重算法', '同权重', '数字大的'], ['权重']),
    5: (['破产场景是否为多条', '多条同时弹'], ['破产时', '同弹']),
    6: (['标签状态'], ['启用', '停用', '已暂停']),
    7: (['「操作」菜单', '菜单里是否有上架'], ['上架']),
    8: (['导出各玩家', '已弹次数导出', '迁移已弹次数', '历史已弹次数'], ['已弹次数', '导出']),
    18: (['服务端判定', '谁来判定', '服务端算', '客户端本地算'], ['上报', '客户端', '服务端']),
    19: (['进入大厅时带上', '带上本次'], ['登录后进入', '从游戏返回']),
    20: (['轮流指针', '轮换池指针', '记住每个弹窗场景', '上次实际弹出的规则'], ['按玩家记住', '指针']),
    21: (['按次记录', '每次触发弹窗场景'], ['返回结果', '数据页']),
    23: (['玩家查询接口'], ['玩家查询', '接收状态']),
    24: (['活动广告页', '弹窗形式'], ['活动本身']),
    25: (['活动类弹窗', '储值类弹窗'], ['同时弹', '每次弹几个']),
    26: (['测试群组', '发送测试要发到'], ['发送测试', '测试账号', '固定不弹']),
    27: (['弹窗设置在后台配', '宣传图改为后台配'], ['宣传图', '弹窗设置', '客户端读取', '自带的图']),
    28: (['活动改期', '开始、结束、改期', '通知推送后台'], ['改期', '活动后台', '礼包后台']),
}


def tag_known(text):
    out = []
    for n, words in STRONG.items():
        hit = [w for w in words if w in text]
        if not hit:
            weak = [w for w in TUOPAIBAN[n][1] if w in text]
            if len(weak) >= 3:
                hit = weak
        if hit:
            out.append('已在待拍板第 %d 件（%s）' % (n, '、'.join(hit[:3])))
    for n, (strong, weak) in YANFA.items():
        hit = [w for w in strong if w in text]
        if not hit:
            wk = [w for w in weak if w in text]
            if len(wk) >= 2 and n not in (4, 6, 7):
                hit = wk
        if hit:
            out.append('已在研发待确认第 %d 条（%s）' % (n, '、'.join(hit[:3])))
    return out


def parse_source(path, src):
    rows = []
    for l in z.rd(path):
        if not re.match(r'^\| %s-\d+ \|' % re.escape(src), l):
            continue
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) < 5:
            continue
        if len(c) > 5:  # 文字里有竖线：合并中间段
            c = [c[0], '／'.join(c[1:-3]), c[-3], c[-2], c[-1]] if False else [c[0], ' '.join(c[1:len(c) - 3]), c[-3], c[-2], c[-1]]
        rows.append(dict(id=c[0], src=src, text=c[1], loc=c[2], sev=c[3], go=c[4], file=path.name))
    return rows


class Resolver:
    def __init__(self):
        self.ch = z.Chain()
        self.fields = {f['code']: f for f in self.ch.fields}
        self.ctrl_text = []
        for r in self.ch.ref:
            self.ctrl_text.append((r, z.norm(r['ctrl'])))
        self.keys = []
        for f in self.ch.fields:
            if f['kind'] == 'F':
                k = z.norm(f['name'].split('·')[-1])
                if len(k) >= 4:
                    self.keys.append((k, f['code']))

    def frame_codes(self, text):
        out = Counter()
        for m in re.finditer(r'框架\s*([L\d–\-、 ,，]+)', text):
            seg = m.group(1)
            for a, b in re.findall(r'L?(\d+)(?:[–\-]L?(\d+))?', seg):
                lo = int(a); hi = int(b) if b else lo
                if hi - lo > 80 or lo < 150:
                    continue
                for code, (ls, _) in self.ch.fl.items():
                    if any(lo <= x <= hi for x in ls):
                        out[code] += 1
        return out

    def resolve(self, row):
        src = row['src']
        text = row['text'] + ' ' + row['loc']
        if src in ('b', 'c'):
            m = re.match(r'〔([^〕]*)〕', row['loc'])
            if m:
                codes = z.CODE_RE.findall(m.group(1))
                if codes:
                    return codes
        votes = Counter()
        if src in ('d1', 'd2'):
            quotes = re.findall(r'「([^」]{2,30})」', row['loc']) + re.findall(r'「([^」]{2,30})」', row['text'])
            pages = [p for p in re.findall(r'\b(\d{1,2}[a-z]?\d?)_[^\s、，；：。（）「」]+', text)]
            for q in quotes:
                nq = z.norm(q)
                if len(nq) < 2:
                    continue
                hits = [r for r, nt in self.ctrl_text if nq in nt]
                if pages:
                    same = [r for r in hits if any(('%s_' % p) in r['page'] for p in pages)]
                    hits = same or hits
                for r in hits:
                    for c in r['codes']:
                        if c in self.fields:
                            votes[c] += 1
        if src in ('d1', 'd2', 'a', 'e'):
            votes.update(self.frame_codes(text))
        if not votes:
            ntext = z.norm(text)
            for k, c in self.keys:
                if k in ntext:
                    votes[c] += 1
        if not votes:
            return []
        top = votes.most_common()
        best = top[0][1]
        return [c for c, v in top if v == best][:3]


def load_prev():
    prev = {}
    if OUT.exists():
        for l in z.rd(OUT):
            if re.match(r'^\| [a-e]\d?-\d+ \|', l):
                c = [x.strip() for x in l.strip().strip('|').split('|')]
                if len(c) >= 8:
                    prev[c[0]] = (c[-2], c[-1])
    return prev


def main():
    res = Resolver()
    rows, counts, missing = [], {}, []
    for src, pat in SRC_GLOB:
        fs = sorted(BEN.glob(pat))
        if not fs:
            missing.append(src); counts[src] = None; continue
        rs = parse_source(fs[0], src)
        counts[src] = len(rs)
        rows += rs
    prev = load_prev()
    for r in rows:
        codes = res.resolve(r)
        r['codes'] = codes
        r['tags'] = tag_known(r['text'] + ' ' + r['loc'])
        go, ft = prev.get(r['id'], ('', ''))
        r['go'] = go if go else r['go']
        r['ft'] = ft
    # 归组
    groups = {}
    for r in rows:
        key = r['codes'][0] if r['codes'] else '—' + r['id']
        r['grp'] = key
        groups.setdefault(key, []).append(r)
    gsorted = sorted(groups.items(), key=lambda kv: (min(SEV.get(x['sev'], 3) for x in kv[1]), kv[0]))
    n_grp = len(groups)
    known_rows = [r for r in rows if r['tags']]
    known_groups = {r['grp'] for r in known_rows}
    known_tp = {r['grp'] for r in rows if any('待拍板' in t for t in r['tags'])}
    known_yf = {r['grp'] for r in rows if any('研发待确认' in t for t in r['tags'])}
    out = ['# 嫌疑总表', '',
           '由 `程序/合并嫌疑.py` 生成；六张清单合并、同链编号归一组。去向、内容定性两列由第二级填（重跑程序会按编号带回已填的）。', '',
           '**各来源条数**：' + '、'.join('%s %s' % (s, ('缺' if counts[s] is None else counts[s])) for s, _ in SRC_GLOB) +
           '；合计 **%d 条**；归并后 **%d 组**（同链编号归一；没找到链编号的每条自成一组，共 %d 条）。' % (
               len(rows), n_grp, sum(1 for r in rows if not r['codes'])),
           '**已在待拍板或研发待确认**（文字匹配，命中词写在括号里，第二级核对）：待拍板 %d 组、研发待确认 %d 组，合计 %d 组 %d 条。'
           % (len(known_tp), len(known_yf), len(known_groups), len(known_rows)),
           ('**还缺**：' + '、'.join(missing) + ' 清单（出来后重跑）。') if missing else '六张清单齐。', '',
           '| 编号 | 来源 | 链编号 | 嫌疑 | 严重度 | 已在待拍板或研发待确认 | 去向（空） | 内容定性（空） |',
           '|---|---|---|---|---|---|---|---|']
    for key, rs in gsorted:
        for r in sorted(rs, key=lambda x: (SEV.get(x['sev'], 3), x['id'])):
            t = r['text'].replace('|', '／').replace('\n', ' ')
            if len(t) > 150:
                t = t[:150] + '…（全文见 %s %s）' % (r['file'][:6], r['id'])
            out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                r['id'], r['src'], '、'.join(r['codes']) or '—', t, r['sev'], '；'.join(r['tags']), r['go'], r['ft']))
    OUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
    empty = sum(1 for r in rows if not r['go'].strip())
    print('来源条数:', {s: counts[s] for s, _ in SRC_GLOB}, '合计', len(rows))
    print('归并后组数:', n_grp, '（无链编号', sum(1 for r in rows if not r['codes']), '条）')
    print('已在待拍板组数:', len(known_tp), '研发待确认组数:', len(known_yf), '两者合计组数:', len(known_groups), '条数:', len(known_rows))
    print('去向为空 %d 条' % empty)
    print('写入', OUT)


if __name__ == '__main__':
    main()
