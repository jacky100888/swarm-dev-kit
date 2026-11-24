---
applyTo: "**"
---

# GitHub Copilot 倉庫級指令 (Swarm Edition)

本倉庫提供一套面向多 AI 編碼助手（Gemini / Claude / Codex / Grok / Cursor / Copilot）的可維護配置與 Swarm 協作體系。你在本倉庫或目標專案內工作時，必須優先遵守以下約定：

## 多模型 Swarm 協作流程

1. **指揮協調 (Gemini)**：拆解需求、管理看板與階段交接。
2. **技術文檔與規格 (Claude)**：產出 `docs/specs/<feature>.spec.md`，鎖定 API 契約、DB Schema 與驗收標準。
3. **核心代碼開發 (Codex)**：依據 `.spec.md` 實作代碼與單元測試，輸出變更清單與測試證據 `docs/specs/<feature>.impl.md`。
4. **雙軌交叉驗收 (Claude + Grok)**：Claude 審查架構與 API 契約一致性，Grok 進行紅隊邊界、併發與漏洞壓力測試，雙軌通過後方可交付。

## 工作方式與品質底線

- 先閱讀相關代碼、規格和腳本，再做最小改動；優先複用既有模式，不擅自擴充需求。
- 前後端聯調異常時，先核對 API 契約與統一回應格式，不以前端容錯長期掩蓋後端失配。
- 嚴禁透過修改測試或開啟全域放行開關（如 `skipLibCheck`、`-DskipTests`、`@ts-nocheck`）掩蓋錯誤。
- 嚴禁保留 TODO/MVP 佔位符；嚴禁在 git commit 添加 Co-Authored-By 或 AI 署名。
- 單檔案行數硬限制：Java ≤ 300、Go ≤ 400、Vue/TSX/JSX ≤ 200、TS/JS/Python ≤ 300。

## 協作與輸出

- CRITICAL: 預設一律使用 **繁體中文（台灣習慣用語，zh-Hant-TW）** 回覆、撰寫註解與 commit message；技術術語、代碼識別符、日誌與協議欄位保持英文原文。
- 文檔和代碼中的作者署名統一使用 `Jacky`（Java 檔案頭註解統一使用 `@author Jacky`）。
