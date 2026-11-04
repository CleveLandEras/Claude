#!/bin/bash
# 入口过期测试：拦下 4 条测试通知（只存不推），1 分钟后用 A、B 各点一条，10 分钟后再用 A、B 各点一条；
# 中间顺带测「切到别的应用」后监听还在不在。用法：tools/age_test.sh <结果文件>
cd "$(dirname "$0")/.."; T=tools/t.sh; ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}
wake() { $ADB shell input keyevent KEYCODE_WAKEUP; $ADB shell wm dismiss-keyguard; $ADB shell input keyevent KEYCODE_HOME; sleep 1; }
check() { wake; $T cmd --es cmd clearours; $T cmd --es cmd repost --ei idx $1 --es mode $2; sleep 1.5
  echo "== $3：#$1 做法$2 $(date +%H:%M:%S)"; $T tap "#$1 做法$2"; $T where 3; $ADB shell input keyevent KEYCODE_HOME; }
t0=$SECONDS
$T cmd --es cmd set --es auto 0 --es cancel 1
for i in 1 2 3 4; do $T post; sleep 1; done
echo "== 拦下 4 条 $(date +%H:%M:%S)"; sleep 2; $T log 40 | grep -E "入队" | cut -c1-120
sleep $((60 - (SECONDS - t0))); check 1 A "过 1 分钟"; check 2 B "过 1 分钟"
wake; $ADB shell am start -a android.settings.SETTINGS >/dev/null; sleep 60
echo "== 切到设置 1 分钟后发一条 $(date +%H:%M:%S)"; $T post; sleep 2; $T log 6 | grep -E "收到|入队" | cut -c1-120; $ADB shell input keyevent KEYCODE_HOME
sleep $((600 - (SECONDS - t0))); check 3 A "过 10 分钟"; check 4 B "过 10 分钟"
echo "== 日志（跳转相关）"; $T log 80 | grep -E "B 已发出|B 跳转失败|打开详情页|监听已" | cut -c1-120
