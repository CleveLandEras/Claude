#!/bin/bash
# M2' 不多加载实测（思考页 7.3 第 5 步、待查 5、8.1 第二条）。子代理里 `claude -p` 报「未登录」，交第一级跑。写法照 软链接实测.sh。
# 问的事：在 ~/claude 下工作时，Claude 读到 _底座/搬家/规则包/ 里的 SKILL.md、子代理文件之后，会不会多出一份技能或子代理。
# 做的事：在 ~/claude 下跑两次 claude -p（钩子关掉；改文件、跑命令、上网的工具都关掉；不留会话记录）：
#   第一次：先用 Read 读规则包里的 skills/开工/SKILL.md 和 agents/总验收人.md，再列出能用的技能和子代理名字；
#   第二次：不读，直接列。
#   两次的列表相同、每个名字只出现一次，就算过。
# 只读：不碰 ~/.claude/ 和 ~/claude/ 里的任何文件，只写 <结果目录>。
# 用法：bash 不多加载实测.sh [结果目录]      不给目录就用 mktemp -d
set -u
L="${1:-$(mktemp -d)}"
mkdir -p "$L"
P="$HOME/claude/_底座/搬家/规则包"
SK="$P/skills/开工/SKILL.md"
AG="$P/agents/总验收人.md"
for f in "$SK" "$AG"; do
  [ -f "$f" ] || { echo "找不到 $f，先跑 导出.sh --执行"; exit 2; }
done
OFF='{"disableAllHooks": true}'
NOWRITE="Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch,Glob,Grep,Task,Agent,Skill"
ASK='列出你现在能用的全部技能名字和全部子代理（agent）类型名字：每行一个，技能行以「技能：」开头，子代理行以「子代理：」开头；同一个名字在你的上下文里出现几次就写几行；只写这些行，不加解释，不要调用技能或子代理。'

cd "$HOME/claude" || exit 1
# 提示词从标准输入传：--allowedTools、--disallowedTools 能接多个值，提示词放在它们后面会被当成工具名吃掉（第二级 11/03 实跑报错）
P1="先用 Read 工具读这两个文件：$SK 和 $AG（只读，不改）。读完先写一行「读到：」，后面照抄这两个文件头部的 name 行。然后：$ASK"
P2="不要调用任何工具。$ASK"
printf '%s' "$P1" | claude -p --model sonnet --no-session-persistence --settings "$OFF" \
  --allowedTools "Read" --disallowedTools "$NOWRITE" > "$L/第一次_读过.txt" 2>&1
echo "第一次（先读规则包里的两个文件）claude -p 退出码 $?；原样回答在 $L/第一次_读过.txt"
printf '%s' "$P2" | claude -p --model sonnet --no-session-persistence --settings "$OFF" \
  --disallowedTools "Read,$NOWRITE" > "$L/第二次_没读.txt" 2>&1
echo "第二次（不读）claude -p 退出码 $?；原样回答在 $L/第二次_没读.txt"

grep -q '读到：' "$L/第一次_读过.txt" && grep -q 'name: *开工' "$L/第一次_读过.txt" \
  && echo "第一次确实读了规则包里的文件（见到 name: 开工）" \
  || echo "第一次没见到「读到：…name: 开工」：可能没读成，这次测法不成立，别下结论"
pick() { grep -E '^[[:space:]]*[-*]?[[:space:]]*(技能|子代理)：' "$1" | sed -E 's/^[[:space:]]*[-*]?[[:space:]]*//; s/[[:space:]]+$//' | sort; }
pick "$L/第一次_读过.txt" > "$L/列表_读过.txt"
pick "$L/第二次_没读.txt" > "$L/列表_没读.txt"
echo "列表：读过 $(wc -l < "$L/列表_读过.txt" | tr -d ' ') 行，没读 $(wc -l < "$L/列表_没读.txt" | tr -d ' ') 行"
[ -s "$L/列表_没读.txt" ] || echo "没读的那次一行都没列出来：这次测法不成立，别下结论"
dup1=$(uniq -d "$L/列表_读过.txt"); dup2=$(uniq -d "$L/列表_没读.txt")
[ -z "$dup1" ] && echo "读过：每个名字只出现一次" || echo "读过：有名字出现不止一次：$(echo $dup1)"
[ -z "$dup2" ] && echo "没读：每个名字只出现一次" || echo "没读：有名字出现不止一次：$(echo $dup2)"
# 规则包里的名字（6 个技能、2 个子代理）逐个看两次各出现几次
for d in "$P"/skills/*/; do n=$(basename "$d"); echo "技能：$n"; done > "$L/规则包名字.txt"
for f in "$P"/agents/*.md; do n=$(sed -n 's/^name: *//p' "$f" | head -1); echo "子代理：$n"; done >> "$L/规则包名字.txt"
while read -r k; do
  a=$(grep -cxF "$k" "$L/列表_读过.txt"); b=$(grep -cxF "$k" "$L/列表_没读.txt")
  echo "$k：读过 $a 次，没读 $b 次"
done < "$L/规则包名字.txt"
if diff "$L/列表_读过.txt" "$L/列表_没读.txt" > "$L/两次差异.txt" && [ -z "$dup1$dup2" ] && [ -s "$L/列表_没读.txt" ]; then
  echo "结论：过（两次列表相同，每个名字只出现一次）"
else
  echo "结论：不过或要人看（差异在 $L/两次差异.txt）。差异只在规则包以外的名字、规则包的名字两次都各 1 次的，多半是模型漏列，交第二级判；"
  echo "      规则包里的名字读过以后变成 2 次、或多出名字的，照待查 5 的退路：规则包里的 skills/、agents/ 改名（如 技能/、子代理/）再测，装上脚本跟着改。"
fi
