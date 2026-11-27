---
description: 啟動 Antigravity Swarm 四階段完整開發流程（Grok 指揮 → Claude 規格 → Claude+Gemini 開發 → Codex 單一驗收）
argument-hint: "功能需求或任務描述"
---

# Antigravity Swarm 四階段開發調度指令

任務目標：「$ARGUMENTS」

請嚴格按照 `swarm-workflow` 技能定義的四階段流水線推進（在 OpenMausBot 中由指揮者透過 `coordinate_bots` 調度 `Claude-Spec`、`Claude-Dev`、`Gemini-Dev`、`Codex-Accept`，每個新任務開新 thread）：

1. **Stage 1 — 指揮拆解 (`grok-4.7`)**
   - 盤點受影響模組，判斷風險等級，列出各開發者可改的檔案。
2. **Stage 2 — 技術規格 (`Claude-Spec` / `claude-opus-5-5[1m]`，大型新系統用 `claude-fable-5-2`)**
   - 產出 `docs/specs/<feature>.spec.md`（範圍、DB Schema、API 契約、檔案分工與行數預算、Acceptance Criteria）。
3. **Stage 3 — 開發 (`Claude-Dev` 主力 + `Gemini-Dev` 協同)**
   - 按風險與獨立性分工，不改同一檔案；合併後跑測試，產出 `docs/specs/<feature>.impl.md`。
4. **Stage 4 — 單一關驗收 (`Codex-Accept` / `gpt-6.2-sol`)**
   - 審查架構、API 契約、防禦規範與邊界反例；Codex 額度用完改 `Grok-QA`。
   - 僅權限、金流、schema migration、併發加派 `Daybreak-Red`，只給高風險 diff。
   - 產出 `docs/specs/<feature>.verify.md`；`FAIL` 退回原開發者，只複驗未通過項目。
