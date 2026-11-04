#!/bin/bash
# 响声压法：等勿扰打开 → 测 a；等勿扰关闭且测试应用的渠道设成静音 → 测 b。用法：tools/mute_chain.sh <证据目录>
cd "$(dirname "$0")/.."; ADB=${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}; EV="$1"; end=$((SECONDS+1700))
imp() { $ADB shell dumpsys notification | grep -E "mName=测试通知," | grep -oE "mImportance=[0-9]" | head -1 | cut -d= -f2; }
until [ "$($ADB shell settings get global zen_mode)" != "0" ]; do sleep 2; [ $SECONDS -gt $end ] && { echo "超时：没等到打开勿扰"; exit 1; }; done
sleep 3; tools/sound_round.sh "a 开勿扰" > "$EV/T5_响声_a勿扰.txt" 2>&1; echo "a 测完"
until [ "$($ADB shell settings get global zen_mode)" = "0" ] && [ "$(imp)" -le 2 ] 2>/dev/null; do sleep 2; [ $SECONDS -gt $end ] && { echo "超时：没等到关勿扰并设静音（渠道重要性=$(imp)）"; exit 1; }; done
sleep 3; tools/sound_round.sh "b 测试应用渠道设静音" > "$EV/T5_响声_b渠道静音.txt" 2>&1; echo "b 测完"
