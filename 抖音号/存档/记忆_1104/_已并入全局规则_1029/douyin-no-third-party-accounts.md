---
name: douyin-no-third-party-accounts
description: Douyin visuals are drawn by Claude in code (Remotion/SVG); user ruled out opening any third-party AI image/voice accounts on 2026-10-28
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5f9ca7f-d384-4fb3-94b0-d8ddaecba3d6
  modified: 2026-10-28T07:09:24.974Z
---

On 2026-10-28 the user rejected the tool-research recommendation (火山方舟 Seedream for images, MiniMax for voice, ~¥120 and two real-name accounts): "不需要开第三方的账号。opus5.5已经足够强大，无数的抖音爆款视频已经证明了这一点。"

**Why:** the user trusts Claude's own code-drawing ability. The closest hits are code-drawable anyway: 西西弗酒馆 (line-art silhouettes, #claude, 50.6万赞), 地图君 (stick figures, 64.7万赞), the Vibe 知识大赏 Remotion hits, and 小克在打工. Code also beats AI image generation on keeping one style and one character across ~60 shots, because the character is a single reused component.

**How to apply:** do not propose third-party image-generation, video-generation or TTS accounts or paid APIs for this account. Draw every shot in code: a style spec in `studio/src/style.ts`, a character component with a clear signature feature, and a growing prop library. Pick styles code does well (line art, silhouette, flat, geometric, pixel). For voiceover, use local open-source TTS such as Qwen3-TTS, or no voiceover. Details are in dy/工具调研_生图与动画.md. Related: [[douyin-self-direction]], [[douyin-editing-not-style]].
