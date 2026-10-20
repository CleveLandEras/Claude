"""执行者用：本轮中途放弃（例如发现暂停.txt）时运行，只释放执行锁、不记录轮次。不带参数运行。"""
from _lock import release
release('executor'); print('执行锁已释放（本轮未计入轮次）')
