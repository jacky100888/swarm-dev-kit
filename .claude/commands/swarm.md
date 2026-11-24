---
description: 啟動 Antigravity Swarm 四階段完整開發流程（Gemini 指揮 → Claude 規格 → Codex 開發 → Claude+Grok 雙軌驗收）
argument-hint: "功能需求或任務描述"
---

# Antigravity Swarm 四階段開發調度指令

任務目標：「$ARGUMENTS」

請嚴格按照 `swarm-workflow` 技能定義的四階段流水線推進（若在 OpenMausBot 中由 Gemini 指揮官執行，請透過 `coordinate_bots` 依序調度 `Claude-Spec`、`Codex-Dev`、`Grok-QA`）：

1. **Stage 1 — Gemini 指揮拆解 (`gemini-4-neon` / `gemini-3.8-flash`)**
   - 盤點受影響模組與現有程式碼結構，建立任務看板與交接計畫。
2. **Stage 2 — Claude 技術規格文檔 (`Claude-Spec` / `claude-opus-5-5[1m]`)**
   - 產出 `docs/specs/<feature>.spec.md`（鎖定範圍、DB Schema、API 契約、檔案行數拆分預算、Acceptance Criteria）。
3. **Stage 3 — Codex 核心代碼開發 (`Codex-Dev` / `gpt-6.2-sol`)**
   - 依據 `.spec.md` 實作完整代碼與單元測試，執行編譯與測試驗證，產出 `docs/specs/<feature>.impl.md`。
4. **Stage 4 — Claude + Grok 雙軌交叉驗收 (`Claude-Spec` + `Grok-QA` / `grok-4.7`)**
   - **Claude 軌**：審查架構一致性、API 契約、防禦規範與行數限制。
   - **Grok 軌**：紅隊挑錯，審查極端邊界、Race Condition 併發競爭、N+1/OOM 與異常回滾漏洞。
   - 產出 `docs/specs/<feature>.verify.md`。雙軌皆 `PASS` 方可交付；任一軌 `FAIL` 則將具體行號與反例退回 Stage 3 Codex 重工。
