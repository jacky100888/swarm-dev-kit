---
description: 功能開發（Swarm Stage 3 - 開發者：依據 Claude 技術規格實作功能、跑測試並輸出交接證據）
argument-hint: "[功能描述 或 docs/specs/<feature>.spec.md 路徑]"
---

> **Swarm Stage 3（開發）**：由 Claude（主力，`claude-opus-5-5`）與 Gemini（協同，`gemini-4-neon`）執行，只改分配給自己的檔案。

功能需求或規格路徑：「$ARGUMENTS」

---

## 執行流程

### 第 1 步：讀取技術規格與既有代碼
1. 若 `docs/specs/` 下已有 Claude（Stage 2）產出的 `.spec.md`，**必須先完整讀取該規格書**，以其 API 契約、DB Schema、檔案拆分表與 Acceptance Criteria 為唯一實作依據。
2. 若尚未有 `.spec.md` 且任務涉及 3+ 檔案或跨模組變更，先按 Stage 2 標準產出簡要規格與拆解計畫。
3. 讀取受影響的既有代碼，確認統一回應格式、錯誤處理與命名風格。

### 第 2 步：防禦性實作（嚴格遵守約束）
- **不留佔位符**：提供完整可執行的代碼，**嚴禁留下 `TODO`、`MVP` 或未實現的空函式**。
- **行數硬限制**：Java ≤ 300、Go ≤ 400、Vue/TSX ≤ 200、TS/JS/Python ≤ 300（排除空行與純註解）。超限前先拆分子模組。
- **禁止掩蓋錯誤**：嚴禁修改既有測試來適配錯誤代碼；嚴禁開啟全域放行開關（如 `skipLibCheck`、`-DskipTests`、`@ts-nocheck`）。
- **作者署名**：新增檔案頭註解統一使用 `Jacky`（如 `@author Jacky`）；git commit 嚴禁添加 `Co-Authored-By` 或 AI 署名。

### 第 3 步：自癒驗證與交接證據輸出（供 Stage 4 驗收）
1. 在終端機實際執行編譯、Linter 與單元測試（如 `go test ./...`、`mvn test`、`npm run build`），若失敗則自癒修復至綠燈。
2. 輸出（或寫入 `docs/specs/<feature>.impl.md`）以下結構化交接清單：
   - **【變更檔案與行數檢查表】**
   - **【Acceptance Criteria 逐項完成對照】**
   - **【測試執行指令與真實終端機輸出證據】**
   - **【請驗收者重點審查區塊與高風險 diff 範圍】**
