# -*- coding: utf-8 -*-
"""草稿展平：同事草稿_活动弹窗规则.xlsx 两张工作表 -> 一行一个「规则块 × 活动或礼包」。

用法：python3 -I 草稿展平.py
输出：本目录 草稿展平.tsv（只读草稿，不改任何文件），并在终端打印汇总。

规则块 = 一个「派发对象」标签所在的表格（标签格右边是值格，下面是 彈窗權重 / 縂彈窗數量 / 彈窗排序 + 5 或 9–10 个格位）。
空格位 = 活动名为「空」或留白，不产生行，只计数。
工作表1 无「活動類/儲值類」分区，类型列记「未分」，再用工作表2 的名字查一次：查到活動類记「活动」，儲值類记「礼包」，都查不到记「未分」。
"""
import os
import re
import zipfile
import xml.etree.ElementTree as ET

XLSX = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/同事草稿_活动弹窗规则.xlsx'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '草稿展平.tsv')
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
USERS = {'新用戶', '全部用戶', '回流用戶', '破產用戶'}
SECTIONS = {'活動類彈窗', '儲值類彈窗'}
EMPTY = {'空', '', None}


def col_to_n(s):
    n = 0
    for ch in s:
        n = n * 26 + ord(ch) - 64
    return n


def n_to_col(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def load_sheets(z):
    ss = []
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall(M + 'si'):
        ss.append(''.join(t.text or '' for t in si.iter(M + 't')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target = {r.get('Id'): r.get('Target') for r in rels}
    sheets = {}
    for sh in wb.iter(M + 'sheet'):
        path = 'xl/' + target[sh.get(R + 'id')]
        sheets[sh.get('name')] = read_sheet(z, path, ss)
    return sheets


def read_sheet(z, path, ss):
    root = ET.fromstring(z.read(path))
    cells = {}
    for c in root.iter(M + 'c'):
        m = re.match(r'([A-Z]+)(\d+)$', c.get('r'))
        col, row = col_to_n(m.group(1)), int(m.group(2))
        t, v = c.get('t'), c.find(M + 'v')
        if t == 's' and v is not None:
            val = ss[int(v.text)]
        elif t == 'inlineStr':
            val = ''.join(x.text or '' for x in c.iter(M + 't'))
        elif v is not None:
            val = v.text
        else:
            continue
        val = val.strip()
        if val:
            cells[(row, col)] = val
    return cells


def find_blocks(cells):
    """每个「派发对象」标签 = 一个规则块。返回列表。"""
    blocks = []
    for (r, c), v in sorted(cells.items()):
        if v != '派发对象':
            continue
        L, V = c, c + 1
        audience = cells.get((r, V))
        if not audience:
            continue
        slots = []
        idx = r + 4
        while True:
            key = cells.get((idx, L))
            if key is None or not re.match(r'^\d+(\.\d+)?$', key):
                break
            slots.append(idx)
            idx += 1
        blocks.append(dict(r=r, L=L, V=V, audience=audience,
                           weight=cells.get((r + 1, V), ''),
                           total=cells.get((r + 2, V), ''),
                           slots=slots))
    return blocks


def section_of(cells, r, L):
    for rr in range(r, 0, -1):
        for cc in (L, 1):
            if cells.get((rr, cc)) in SECTIONS:
                return cells[(rr, cc)]
    return ''


def user_of(cells, r):
    for rr in range(r, 0, -1):
        if cells.get((rr, 1)) in USERS:
            return cells[(rr, 1)]
    return ''


def main():
    with zipfile.ZipFile(XLSX) as z:
        sheets = load_sheets(z)
    flat = []   # 每行一个 dict
    stats = {}
    for sname in ['工作表1', '工作表2']:
        cells = sheets[sname]
        blocks = find_blocks(cells)
        n_blocks, n_rows, n_empty = len(blocks), 0, 0
        for b in blocks:
            r, L, V = b['r'], b['L'], b['V']
            sec = section_of(cells, r, L) if sname == '工作表2' else ''
            usr = user_of(cells, r) if sname == '工作表2' else ''
            block_id = 'S%s-R%d-%s' % (sname[-1], r, n_to_col(V))
            for idx in b['slots']:
                name = cells.get((idx, V), '')
                if name in EMPTY or name == '空':
                    n_empty += 1
                    continue
                cnt = cells.get((idx, V + 3), '')
                cool = cells.get((idx, V + 4), '')
                flat.append(dict(
                    表=sname, 块ID=block_id, 区段=sec or '工作表1未分',
                    用户类型=usr, 派发对象=b['audience'],
                    块权重=b['weight'], 块總彈窗數量=b['total'],
                    排序=cells.get((idx, L), ''), 草稿行=str(idx),
                    活动或礼包=name,
                    弹出时机=cells.get((idx, V + 1), ''),
                    弹窗形式=cells.get((idx, V + 2), ''),
                    每日次数=cnt, 冷却秒=cool,
                    块内签名=(b['weight'], b['total'], tuple(
                        (cells.get((s, V), ''), cells.get((s, V + 1), ''),
                         cells.get((s, V + 2), ''), cells.get((s, V + 3), ''),
                         cells.get((s, V + 4), '')) for s in b['slots'])),
                ))
                n_rows += 1
        stats[sname] = dict(blocks=n_blocks, rows=n_rows, empty=n_empty)

    # 工作表2 的活动/礼包名，用来给工作表1 的行定类型
    s2_act = {f['活动或礼包'] for f in flat if f['表'] == '工作表2' and f['区段'] == '活動類彈窗'}
    s2_gift = {f['活动或礼包'] for f in flat if f['表'] == '工作表2' and f['区段'] == '儲值類彈窗'}
    for f in flat:
        if f['表'] == '工作表1':
            if f['活动或礼包'] in s2_act:
                f['类型'] = '活动（按工作表2 名字定）'
            elif f['活动或礼包'] in s2_gift:
                f['类型'] = '礼包（按工作表2 名字定）'
            else:
                f['类型'] = '未分'
        else:
            f['类型'] = '活动' if f['区段'] == '活動類彈窗' else '礼包'

    # 工作表1 整块重复检查
    s1_blocks = {}
    for f in flat:
        if f['表'] == '工作表1':
            s1_blocks.setdefault(f['块ID'], f['块内签名'])
    dup = {}
    keys = list(s1_blocks)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if s1_blocks[a] == s1_blocks[b]:
                dup[b] = a
    for f in flat:
        f['与前块重复'] = dup.get(f['块ID'], '')
        del f['块内签名']

    cols = ['表', '块ID', '区段', '类型', '用户类型', '派发对象', '块权重', '块總彈窗數量',
            '排序', '草稿行', '活动或礼包', '弹出时机', '弹窗形式', '每日次数', '冷却秒', '与前块重复']
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for f in flat:
            fh.write('\t'.join(str(f[c]) for c in cols) + '\n')

    print('输出：%s' % OUT)
    for s, st in stats.items():
        print('%s：规则块 %d 块，非空行 %d 行，空格位 %d 个' % (s, st['blocks'], st['rows'], st['empty']))
    print('工作表1 整块重复：' + ('；'.join('%s 与 %s 完全相同' % (b, a) for b, a in dup.items()) or '无'))
    print('合计：规则块 %d 块，行 %d 行；去掉工作表1 重复块后 %d 行' % (
        sum(st['blocks'] for st in stats.values()), len(flat),
        len([f for f in flat if not f['与前块重复']])))


if __name__ == '__main__':
    main()
