#!/bin/bash
# M1c 软链接实测（思考页 7.2「M1c」、待查 1、2）。子代理里 `claude -p` 报「Not logged in」，交第一级跑。
# 做的事：在一个临时文件夹建测试项目，CLAUDE.md、.claude/agents/链接测试.md、.claude/skills/链接测试/ 都是指向项目外的软链接，
#        另放一个实体子代理、一个实体技能作对照；在项目里跑一次 claude -p（钩子关掉、读写工具关掉），按标记判三样认不认。
# 不碰 ~/.claude/，不改任何规则文件；只写 <测试目录>。
# 用法：bash 软链接实测.sh [测试目录]      不给目录就用 mktemp -d
set -u
L="${1:-$(mktemp -d)}"
rm -rf "$L/外部" "$L/项目"
mkdir -p "$L/外部/skill" "$L/项目/.claude/agents" "$L/项目/.claude/skills/实体对照"
printf '链接测试标记：青柠-7391。这是项目 CLAUDE.md 的第一行，经软链接放进来。\n' > "$L/外部/CLAUDE.md"
printf -- '---\nname: 链接测试代理\ndescription: 软链接放进来的子代理，标记 橘子-5520。\n---\n只回答「链接测试代理在」。\n' > "$L/外部/agent.md"
printf -- '---\nname: 链接测试技能\ndescription: 软链接放进来的技能，标记 葡萄-8813。\n---\n只回答「链接测试技能在」。\n' > "$L/外部/skill/SKILL.md"
printf -- '---\nname: 实体对照代理\ndescription: 实体文件子代理（对照组），标记 苹果-1100。\n---\n只回答「对照代理在」。\n' > "$L/项目/.claude/agents/实体对照.md"
printf -- '---\nname: 实体对照技能\ndescription: 实体文件技能（对照组），标记 香蕉-2200。\n---\n只回答「对照技能在」。\n' > "$L/项目/.claude/skills/实体对照/SKILL.md"
ln -s ../外部/CLAUDE.md "$L/项目/CLAUDE.md"
ln -s ../../../外部/agent.md "$L/项目/.claude/agents/链接测试.md"
ln -s ../../../外部/skill "$L/项目/.claude/skills/链接测试"

cd "$L/项目" || exit 1
claude -p --model sonnet --settings '{"disableAllHooks": true}' \
  --disallowedTools "Read,Bash,Glob,Grep,Write,Edit,WebFetch,WebSearch" --max-turns 2 \
  "不要调用任何工具，只凭你已有的上下文回答三件事：1) 列出你能派的子代理（agent）类型里名字带「链接测试」或「实体对照」的，连同描述里的标记；2) 列出你能用的技能里名字带「链接测试」或「实体对照」的，连同描述里的标记；3) 你的上下文里有没有一行以「链接测试标记」开头的项目 CLAUDE.md 内容？有就原样复述那一行，没有就说没有。没有的项明确写「没有」。" \
  > "$L/结果.txt" 2>&1
echo "claude -p 退出码 $?；原样回答存在 $L/结果.txt"
judge() { grep -q "$2" "$L/结果.txt" && echo "认：$1（见到标记 $2）" || echo "不认或没列出：$1（没见到标记 $2）"; }
judge '对照：实体子代理' 苹果-1100
judge '对照：实体技能' 香蕉-2200
judge '软链接子代理' 橘子-5520
judge '软链接技能' 葡萄-8813
judge '软链接的项目 CLAUDE.md' 青柠-7391
echo '对照两项不认＝这次测法不成立，别下结论；对照都认时，软链接三项各按上面判（思考页 7.2 M1c：子代理不认→两个子代理改走「装上脚本生成拷贝 + 自检比 sha」；CLAUDE.md 不认→待查 2 的退路）。'
