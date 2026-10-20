#!/bin/zsh
# usage: pl_pptx渲染.sh deck.pptx outdir
# PowerPoint 有沙盒，每换一个文件夹都要 Dk 重新授权。所以只用固定位置 _versions/渲染/：
# 先把 deck 复制成 渲染/render.pptx，在同一文件夹导出 render.pdf，再转成逐页 jpg 放到 outdir。
# 10/14 加锁：多个对话共用这个位置，用 渲染/.lock 排队，最多等 15 分钟；锁超过 10 分钟视为残留。
BASE=/Users/decheng.huang/claude/弹窗标签推送系统
R=$BASE/_versions/渲染
IN=$1; OUT=$2
mkdir -p $R
for i in {1..180}; do
  if mkdir $R/.lock 2>/dev/null; then break; fi
  if [[ -n $(find $R/.lock -maxdepth 0 -mmin +10 2>/dev/null) ]]; then rmdir $R/.lock 2>/dev/null; continue; fi
  sleep 5
done
trap 'rmdir $R/.lock 2>/dev/null' EXIT
rm -rf $OUT; mkdir -p $OUT
cp "$IN" $R/render.pptx; rm -f $R/render.pdf
osascript <<OSA
with timeout of 180 seconds
tell application "Microsoft PowerPoint"
	open (POSIX file "$R/render.pptx")
	delay 3
	set p to presentation "render.pptx"
	save p in (POSIX file "$R/render.pdf") as save as PDF
	delay 1
	close p saving no
end tell
end timeout
OSA
swift $BASE/_scripts/pl_pdf转图.swift $R/render.pdf $OUT
