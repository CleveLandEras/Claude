#!/bin/bash
# 真实应用（三星日历）入口测试：建两个测试日程 X、Y，提醒被拦下后——过 1 分钟 A 点 X、B 点 Y；过 10 分钟 B 点 X、A 点 Y；
# 把日历从最近任务里划掉后 A 点 X、B 点 Y；同时查 X、Y 会不会串台。最后删掉测试日程。用法：tools/cal_age_test.sh
cd "$(dirname "$0")/.."; T=tools/t.sh; ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}
wake() { $ADB shell input keyevent KEYCODE_WAKEUP; $ADB shell wm dismiss-keyguard; $ADB shell input keyevent KEYCODE_HOME; sleep 1; }
check() { wake; $T cmd --es cmd clearours; $T cmd --es cmd repost --ei idx $1 --es mode $2; sleep 1.5
  echo "== $3：$4 #$1 做法$2 $(date +%H:%M:%S)"; $T tap "#$1 做法$2"; $T where 4; $ADB shell input keyevent KEYCODE_HOME; sleep 1; }
idx_of() { $T log 80 | grep -E "入队 \| #[0-9]+ \| 日历 \| $1" | head -1 | grep -oE "#[0-9]+" | head -1 | tr -d '#'; }
$T cmd --es cmd set --es watch "com.dk.notitest,com.samsung.android.calendar" --es cancel 1 --es auto 0; $ADB logcat -c
now=$(( $($ADB shell date +%s | tr -d '\r') * 1000 ))
for x in "cal-age-x:$((now+80000))" "cal-age-y:$((now+110000))"; do name=${x%%:*}; ts=${x##*:}
  $ADB shell content insert --uri content://com.android.calendar/events --bind calendar_id:i:1 --bind title:s:$name --bind dtstart:l:$ts --bind dtend:l:$((ts+1800000)) --bind eventTimezone:s:Asia/Shanghai --bind hasAlarm:i:1
  id=$($ADB shell content query --uri content://com.android.calendar/events --projection _id --where "title=\'$name\'" | grep -oE "_id=[0-9]+" | tail -1 | cut -d= -f2)
  $ADB shell content insert --uri content://com.android.calendar/reminders --bind event_id:i:$id --bind minutes:i:0 --bind method:i:1
  echo "建了日程 $name，提醒时间 $(date -r $((ts/1000)) +%H:%M:%S)"; done
sleep 125; t0=$SECONDS; X=$(idx_of cal-age-x); Y=$(idx_of cal-age-y)
echo "== 拦下：X=#$X Y=#$Y $(date +%H:%M:%S)"; $T log 80 | grep -E "已收起 \| 0\|com.samsung.android.calendar" | sed -E 's/^.*RELAY   \([0-9]+\): //' | cut -c1-110
[ -z "$X" ] || [ -z "$Y" ] && { echo "没拦到两条提醒，停止"; exit 1; }
sleep 45; check $X A "过 1 分钟" X; check $Y B "过 1 分钟" Y
sleep $((600 - (SECONDS - t0))); check $X B "过 10 分钟" X; check $Y A "过 10 分钟" Y
wake; echo "== 划掉日历前：进程=$($ADB shell pidof com.samsung.android.calendar || echo 不在)"
$ADB shell input keyevent KEYCODE_APP_SWITCH; sleep 2; $ADB shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; $ADB exec-out cat /sdcard/ui.xml > /tmp/msgassist_ui.xml
xy=$(python3 -I - /tmp/msgassist_ui.xml <<'PY'
import sys,re,xml.etree.ElementTree as ET
for n in ET.parse(sys.argv[1]).getroot().iter('node'):
    d=(n.get('content-desc') or '')
    if d.startswith('日历'):
        x1,y1,x2,y2=map(int,re.findall(r'\d+',n.get('bounds'))); print((x1+x2)//2,(y1+y2)//2); break
PY
)
echo "日历卡片位置：$xy"; [ -n "$xy" ] && $ADB shell input swipe ${xy% *} ${xy#* } ${xy% *} 150 200; sleep 3; $ADB shell input keyevent KEYCODE_HOME
echo "== 划掉日历后：进程=$($ADB shell pidof com.samsung.android.calendar || echo 不在) 最近任务里还有=$($ADB shell dumpsys activity recents | grep -c 'com.samsung.android.calendar')"
check $X A "日历被划掉后" X; check $Y B "日历被划掉后" Y
$T log 40 | grep -E "B 已发出|B 跳转失败" | sed -E 's/^.*RELAY   \([0-9]+\): //' | cut -c1-100
for name in cal-age-x cal-age-y; do $ADB shell content delete --uri content://com.android.calendar/events --where "title=\'$name\'"; done
echo "测试日程已删：剩余 $($ADB shell content query --uri content://com.android.calendar/events --projection title | grep -c cal-age) 个"
