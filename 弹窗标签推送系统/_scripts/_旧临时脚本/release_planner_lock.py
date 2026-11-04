"""执行者误运行 should_plan.py 占了规划锁时用：只释放 planner 锁，不改规划状态。不带参数运行。"""
from _lock import release
release('planner')
print('已释放规划锁（planner.lock）')
