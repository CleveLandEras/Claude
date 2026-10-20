"""执行者用：每轮开始时运行。上一轮仍在进行则输出「占用」，本轮应立即结束。不带参数运行。"""
from _lock import acquire
ok, t = acquire('executor', 60)
print('结论：', '获得锁，开始本轮' if ok else f'占用（上一轮 {t} 开始，仍在进行），本轮立即结束')
