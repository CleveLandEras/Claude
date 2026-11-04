#!/bin/bash
# 收尾链：等 Dk 给原型放开后台限制 → 自动重启并看监听能否自己连上 → 等 Dk 开勿扰测 a → 等关勿扰并把测试应用渠道设静音测 b。
cd "$(dirname "$0")/.."; ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}; EV="$1"; end=$((SECONDS+1750))
live() { $ADB shell dumpsys notification | awk '/Live notification listeners/{f=1} f&&/msgrelay/{c++} /Notification assistant|Snoozed/{if(f)exit} END{print c+0}'; }
freed() { $ADB shell cmd appops get com.dk.msgrelay RUN_ANY_IN_BACKGROUND | grep -q allow || $ADB shell dumpsys deviceidle whitelist | grep -q msgrelay; }
imp() { $ADB shell dumpsys notification | grep -E "mName=测试通知," | grep -oE "mImportance=[0-9]" | head -1 | cut -d= -f2; }
wait_for() { until eval "$1"; do sleep 3; [ $SECONDS -gt $end ] && { echo "超时：$2"; exit 1; }; done; }
wait_for freed "没等到放开后台限制"
{ echo "== $(date +%H:%M:%S) 已放开：后台运行=$($ADB shell cmd appops get com.dk.msgrelay RUN_ANY_IN_BACKGROUND | tr -d '\n') 电池白名单=$($ADB shell dumpsys deviceidle whitelist | grep -c msgrelay)"
  sleep 5; $ADB reboot; sleep 5; $ADB wait-for-device
  until [ "$($ADB shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do sleep 2; done
  echo "== 开机完成 $(date +%H:%M:%S)"; sleep 40
  echo "== $(date +%H:%M:%S)：监听在连接名单里=$(live) 进程=$($ADB shell pidof com.dk.msgrelay || echo 不在)"
  $ADB logcat -d | grep -E "Force stopping com.dk.msgrelay|isRestricted by MARs! target : com.dk.msgrelay|Process [0-9]+ created for com.dk.msgrelay" | cut -c1-150
  $ADB shell cmd notification post -t "重启后测试" rebootcheck7 "放开限制后重启第一条" >/dev/null; sleep 3
  $ADB shell run-as com.dk.msgrelay cat files/log.txt | tail -3 | sed -E 's/ \| key=.*//; s/ \| 正文=.*//' | cut -c1-120
} > "$EV/T7_重启_放开限制后.txt" 2>&1; echo "重启测完"
wait_for '[ "$($ADB shell settings get global zen_mode)" != "0" ]' "没等到打开勿扰"
sleep 3; tools/sound_round.sh "a 开勿扰" > "$EV/T5_响声_a勿扰.txt" 2>&1; echo "a 测完"
wait_for '[ "$($ADB shell settings get global zen_mode)" = "0" ] && [ "$(imp)" -le 2 ] 2>/dev/null' "没等到关勿扰并设静音"
sleep 3; tools/sound_round.sh "b 测试应用渠道设静音" > "$EV/T5_响声_b渠道静音.txt" 2>&1; echo "b 测完"
