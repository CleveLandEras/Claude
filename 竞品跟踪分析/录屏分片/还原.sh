#!/bin/bash
# 还原竞品录屏：把本目录的分片按顺序拼回原件，放到上一级（竞品跟踪分析/），并核 sha256；不符就报错、不留半成品。
# 用法：bash 竞品跟踪分析/录屏分片/还原.sh
set -u
D="$(cd "$(dirname "$0")" && pwd -P)"
OUT="$(cd "$D/.." && pwd -P)"
LISTF="$D/分片sha256.txt"
[ -f "$LISTF" ] || { echo "缺 $LISTF"; exit 2; }
fail=0
# 先核每个分片自己的 sha256
if ! (cd "$D" && grep -v '^原件:' "$LISTF" | grep -v '^#' | shasum -a 256 -c --quiet - ); then
  echo "分片损坏或缺失，停止"; exit 1
fi
while read -r tag sha name size; do
  [ "$tag" = "原件:" ] || continue
  tmp="$OUT/$name.还原中"
  cat "$D/$name".part-* > "$tmp" || { echo "拼接失败 $name"; rm -f "$tmp"; fail=1; continue; }
  got="$(shasum -a 256 "$tmp" | cut -d' ' -f1)"
  if [ "$got" = "$sha" ]; then mv "$tmp" "$OUT/$name"; echo "还原成功 $name"; else echo "sha256 不符 $name"; rm -f "$tmp"; fail=1; fi
done < "$LISTF"
exit $fail
