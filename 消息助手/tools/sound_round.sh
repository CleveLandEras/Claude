#!/bin/bash
# 响声一轮（亮屏下）：测试应用发一条（被收起）→ 3 秒后我们重推 → 读系统的响铃判定和声音播放起止。
# 用法：tools/sound_round.sh <标签> [q]   带 q 时测试应用发到本来就是静音的渠道（模拟用户把原应用渠道设成静音）
cd "$(dirname "$0")/.."; T=tools/t.sh; ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}
echo "== $1 $(date +%H:%M:%S) 响铃模式=$($ADB shell settings get global mode_ringer)(2=响铃) 勿扰=$($ADB shell settings get global zen_mode)(0=关)"
$ADB shell input keyevent KEYCODE_WAKEUP; $ADB shell wm dismiss-keyguard; $ADB shell input keyevent KEYCODE_HOME
$T cmd --es cmd clearours; sleep 1; start=$($ADB shell 'date "+%H:%M:%S"'); $ADB logcat -b all -c
if [ "$2" = q ]; then $T postq; else $T post; fi; sleep 3; $T cmd --es cmd flush; sleep 4
$T log 20 | grep -E "收到|已收起|重推" | sed -E 's/^.*RELAY   \([0-9]+\): //; s/ \| 正文=.*\| 渠道=/ | 渠道=/' | cut -c1-140
echo "-- 系统响铃判定（1=播放；其他数字=没播，数字是原因码）"
$ADB logcat -b events -d | grep notification_alert | sed -E 's/^[0-9-]+ ([0-9:.]+).*notification_alert: \[[0-9]+\|([^|]+)\|([^|]+)\|[^,]+,([0-9]+),([0-9]+),([0-9]+).*/\1 \2 #\3 震动=\4 响铃=\5/'
echo "-- 通知声音播放起止（$start 之后新建的播放器）"
$ADB shell dumpsys audio > /tmp/msgassist_audio.txt
for p in $(grep -E "player piid:[0-9]+ new .*USAGE_NOTIFICATION" /tmp/msgassist_audio.txt | awk -v s="$start" '$2 >= s' | grep -oE "piid:[0-9]+"); do
  grep -E "$p (new|event:started|event:stopped)" /tmp/msgassist_audio.txt | grep -vE "event:device" | sed -E 's/ AudioAttributes.*//' | cut -c1-70; done
