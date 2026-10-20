# 弹窗标签推送系统

- 开工第一件事：`git fetch origin`，比较 main 与远端各 `claude/*` 分支的最新提交，从最新的那支接着做（主分支可能落后于正在进行的会话分支；10/20 有会话从旧的主分支开工，整轮做在旧版上）。
- 回复用中文。新对话先读 `先看这里.md` 顶部「当前状态与交接」，再读 `规则与交接/标准体系.md` 第〇节（规则入口）。
- 与 Dk 协作的工作习惯与原则：`规则与交接/记忆_快照/`（`MEMORY.md` 是索引）。这是本机记忆 10/20 的快照；云端会话按它工作，改了要告诉 Dk 同步回本机。
- 汇报格式技能在 `.claude/skills/report-format/`。
- 文档里写的 `/Users/decheng.huang/claude/弹窗标签推送系统` 指本仓库根目录；`_scripts/` 下的脚本已改为按自身位置找项目目录。
- 只能在 Dk 的 Mac 上用的工具：`_scripts/pl_pptx渲染.sh`、`_scripts/pl_网页截图.swift`（渲染、截图）。云端截图用 `node _scripts/pl_评审版截图.mjs`（Playwright；先 `apt-get install -y fonts-noto-cjk` 装中文字体）。
- 仓库只放接着干活要用的上下文，不放的内容见 `.gitignore`（旧版本、截图、旧临时脚本、已作废的归档）。
