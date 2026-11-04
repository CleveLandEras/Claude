#!/bin/zsh
# 用法：watch.sh 编号_短名 宽 高 视频地址文件
# 地址文件两行：第一行视频，第二行音频（可空）
set -e
S=/private/tmp/claude-502/-Users-decheng-huang-Documents-dy/ff5e47e0-09d9-42c5-9363-0b905c3841c7/scratchpad
FF=/Users/decheng.huang/Documents/dy/.venv/lib/python3.9/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1
PY=/Users/decheng.huang/Documents/dy/.venv/bin/python
NAME=$1; W=$2; H=$3; URLS=$4
D=$S/vids/$NAME
mkdir -p $D
VURL=$(sed -n 1p $URLS); AURL=$(sed -n 2p $URLS)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
curl -sS -L --fail -A "$UA" -e "https://www.douyin.com/" -o $D/v.mp4 "$VURL"
[ -n "$AURL" ] && curl -sS -L --fail -A "$UA" -e "https://www.douyin.com/" -o $D/a.mp4 "$AURL"
ls -la $D | tail -n +2
if [ $W -ge $H ]; then SC="scale=240:-2"; T1=6x5; T8=6x5; else SC="scale=-2:240"; T1=10x3; T8=10x3; fi
# 开头 30 秒，每秒 1 帧
$FF -v error -y -i $D/v.mp4 -t 30 -vf "fps=1,$SC,tile=$T1:padding=4:color=white" -frames:v 1 $D/open.png
# 全片每 8 秒 1 帧，每 30 张一页
$FF -v error -y -i $D/v.mp4 -vf "fps=1/8,$SC,tile=$T8:padding=4:color=white" $D/full_%02d.png
ls $D/*.png
[ -n "$AURL" ] && $PY -I $S/bin/voice.py $D/a.mp4 || $PY -I $S/bin/voice.py $D/v.mp4
