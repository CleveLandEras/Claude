"""打印本机当前时间。需要在任何文件里写时间时，先运行它，用它的输出，不要自己估。不带参数运行。"""
import datetime
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
