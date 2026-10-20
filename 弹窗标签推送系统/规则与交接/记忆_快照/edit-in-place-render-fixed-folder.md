---
name: edit-in-place-render-fixed-folder
description: "Edit files in place (no defensive copies or per-edit backups); render pptx only via _scripts/pl_pptx渲染.sh in the fixed folder 弹窗标签推送系统/_versions/渲染/ — new locations trigger permission prompts Dk must click (merged 10/16 from edit-directly-no-copies + powerpoint-render-fixed-folder)"
metadata:
  type: feedback
---

**Edit in place.** Don't copy or back up files before working on them. Dk 10/10, after I copied the deck to a temp name before rendering and kept backing up files: 「不用复制，别太浪费token了，直接改动就好」.

**Render in one fixed folder.** Export .pptx to PDF through PowerPoint only by copying into `/Users/decheng.huang/claude/弹窗标签推送系统/_versions/渲染/` (as render.pptx) and saving the PDF there — use `_scripts/pl_pptx渲染.sh` (its internal copy is required by PowerPoint permissions, not a backup). Never open or save from scratchpad or other new paths. Dk 10/10: 「因为你总是要新位置的权限，我每次都要重新给你授予」 — PowerPoint is sandboxed; each new folder pops a grant dialog that blocks further AppleEvents (errors -9074 / -1712) until Dk clicks it. If an export times out, a dialog is probably pending: tell Dk once, don't retry elsewhere. PDF → jpg with `_scripts/pl_pdf转图.swift`.
