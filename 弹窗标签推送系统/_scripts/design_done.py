"""设计者用：本次设计结束时运行，释放设计锁。不带参数运行。"""
from _lock import release
release('designer'); print('设计锁已释放')
