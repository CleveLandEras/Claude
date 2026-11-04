#!/bin/bash
# 锁屏 30 分钟：测试应用在前台时设好 30 分钟定时 → 假装拔电、灭屏、强制进入省电休眠 → 31 分钟时再用系统 shell 发一条；
# 看监听服务收没收到、晚了多久、批次有没有按时推、原通知有没有点亮屏幕。用法：tools/lock_test.sh
cd "$(dirname "$0")/.."; T=tools/t.sh; ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}
wake() { $ADB shell input keyevent KEYCODE_WAKEUP; $ADB shell wm dismiss-keyguard; $ADB shell input keyevent KEYCODE_HOME; }
wake; $ADB logcat -c
$T cmd --es cmd set --es auto 1 --ei window 30 --ei count 3 --es cancel 1 --es watch "com.tencent.mm,com.dk.notitest,com.samsung.android.messaging,com.android.shell,*3"
$T cmd --es cmd clearours; start=$($ADB shell 'date "+%m-%d %H:%M:%S"')
$ADB shell am start -n com.dk.notitest/.MainActivity >/dev/null; sleep 2; $T later 30; sleep 2
echo "== 开始 $start：30 分钟定时已设好=$($ADB logcat -d -s NTEST:I | grep -c '定时')"
$ADB shell input keyevent KEYCODE_HOME; sleep 1
$ADB shell dumpsys battery unplug; $ADB shell input keyevent KEYCODE_SLEEP; sleep 5
echo "强制休眠：$($ADB shell dumpsys deviceidle force-idle 2>&1 | tr '\n' ' ')"
caffeinate -i sleep 1860
echo "== $(date +%H:%M:%S) 第 31 分钟：用系统 shell 再发一条"
$ADB shell cmd notification post -t "锁屏测试" lockcheck "锁屏31分钟时系统发的一条" >/dev/null
caffeinate -i sleep 60
echo "== $(date +%H:%M:%S)：省电休眠状态=$($ADB shell dumpsys deviceidle | grep -m1 -oE 'mState=[A-Z_]+') 监听进程=$($ADB shell pidof com.dk.msgrelay || echo 不在)"
echo "监听在连接名单里=$($ADB shell dumpsys notification | awk '/Live notification listeners/{f=1} f&&/msgrelay/{c++} /Notification assistant|Snoozed/{if(f)exit} END{print c+0}')"
$ADB shell run-as com.dk.msgrelay cat files/log.txt | awk -v s="$start" '$1" "$2 >= s' | grep -vE "设置|清掉" | sed -E 's/ \| key=.*\| 亮屏=/ | 亮屏=/; s/ \| 入口=.*//' | cut -c1-160
echo "-- 测试应用：$($ADB logcat -d -s NTEST:I | grep -E '发出' | tail -1 | cut -c1-80)"
$ADB shell dumpsys deviceidle unforce >/dev/null; $ADB shell dumpsys battery reset; wake
echo "== 已恢复：退出强制休眠、恢复真实电源状态"
