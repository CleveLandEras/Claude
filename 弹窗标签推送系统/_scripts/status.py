"""打印每份阶段产出与呈交版的状态（按文件内容现算）。不带参数运行。
状态只认本脚本的输出：「已过审」＝内容与最近一次过审时一致；「待复核」＝过审后有改动；「未过审」＝没有过审记录。
任何角色不得在推进计划、产出页首或简报里手写与本脚本不一致的状态。"""
from state_lib import tracked, status, load

store = load()
print('| 文件 | 状态 | 说明 |')
print('|---|---|---|')
for name in tracked():
    st, note = status(name, store)
    print(f'| {name} | {st} | {note} |')
