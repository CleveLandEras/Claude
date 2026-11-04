#!/bin/bash
# 测试用 adb 小工具。用法：tools/t.sh <子命令> [参数]
#   log [行数]        看原型(RELAY)和测试应用(NTEST)的最近日志
#   cmd <参数...>     给原型下调试指令，例：cmd --es cmd repost --ei idx 3 --es mode B
#   post | later 分钟 让测试应用马上发一条 / 过几分钟发一条
#   tap <文字>        拉下通知栏，点包含这段文字的那条通知
#   where             当前前台页面 + 屏幕上的文字（判断落到了哪个聊天）
#   shot <文件>       截图存到文件
ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}
UI=${TMPDIR:-/tmp}/msgassist_ui.xml

dump() { $ADB shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; $ADB exec-out cat /sdcard/ui.xml > "$UI"; }

parse() {
python3 -I - "$@" <<'EOF'
import sys, re, xml.etree.ElementTree as ET
mode, path = sys.argv[1], sys.argv[2]
try:
    nodes = list(ET.parse(path).getroot().iter('node'))
except Exception as e:
    print('界面读取失败', e); sys.exit(0)
if mode == 'find':
    for n in nodes:
        t = (n.get('text') or '') + ' ' + (n.get('content-desc') or '')
        if sys.argv[3] in t:
            x1, y1, x2, y2 = map(int, re.findall(r'\d+', n.get('bounds')))
            print((x1 + x2) // 2, (y1 + y2) // 2); break
else:
    out = []
    for n in nodes:
        t = (n.get('text') or '').strip()
        if t and t not in out: out.append(t)
    print(' / '.join(out[:int(sys.argv[3])]))
EOF
}

case "$1" in
  log) $ADB logcat -d -v time -s RELAY:I NTEST:I | sed -E 's/ [IWE]\/(RELAY|NTEST)\( *[0-9]+\): / \1 /; s/RELAY [0-9-]+ [0-9:.]+ \|/RELAY |/' | tail -n "${2:-30}" ;;
  cmd) shift; $ADB shell am broadcast -n com.dk.msgrelay/.CmdReceiver "$@" >/dev/null ;;
  post) $ADB shell am broadcast -f 0x10000000 -n com.dk.notitest/.PostReceiver --es from adb >/dev/null ;;
  postq) $ADB shell am broadcast -f 0x10000000 -n com.dk.notitest/.PostReceiver --es from adb --ez quiet true >/dev/null ;;
  later) $ADB shell am broadcast -f 0x10000000 -n com.dk.notitest/.PostReceiver --ei later "$2" >/dev/null ;;
  tap)
    $ADB shell cmd statusbar expand-notifications; sleep 1.5; dump
    xy=$(parse find "$UI" "$2")
    if [[ "$xy" =~ ^[0-9]+\ [0-9]+$ ]]; then $ADB shell input tap $xy; echo "已点：$2"; else echo "没找到：$2 $xy"; $ADB shell cmd statusbar collapse; fi ;;
  where)
    sleep 1.5
    $ADB shell dumpsys activity activities | grep -m1 -E "topResumedActivity|mResumedActivity" | sed -E 's/.*\{[^ ]+ [^ ]+ ([^ ]+).*/前台页面：\1/'
    dump; echo "屏幕文字：$(parse texts "$UI" "${2:-12}")" ;;
  shot) $ADB exec-out screencap -p > "$2" && echo "截图：$2" ;;
  *) sed -n '2,9p' "$0" ;;
esac
