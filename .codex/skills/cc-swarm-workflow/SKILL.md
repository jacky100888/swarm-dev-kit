---
name: cc-swarm-workflow
description: Antigravity Swarm 四階段多模型協作工作流（Grok 指揮 → Claude 規格 → Claude+Gemini 開發 → Codex 單一驗收，高風險加紅隊）的標準產物契約與交接規範。
version: 3.0.0
---

# Antigravity Swarm 四階段多模型協作工作流

本技能定義多模型團隊（Grok + Claude + Gemini + Codex）在開發新功能、架構重構與複雜排障時的**職責邊界、交接產物格式（Artifact Contract）與驗收標準**。

---

## 一、四階段角色與模型配置

| 階段 | 角色 | 推薦模型 | 核心輸入 | 強制交接產物 (Artifact) |
|------|------|----------|----------|------------------------|
| **Stage 1** | **指揮協調者 (Coordinator)** | Grok (`grok-4.7`) | 使用者原始需求 | 任務拆解、風險等級、派工 |
| **Stage 2** | **技術文檔與規格 (Architect)** | Claude (`claude-opus-5-5[1m]`；僅全新系統或大型重構用 `claude-fable-5-2`) | 階段 1 派工 + 既有代碼庫 | `docs/specs/<feature>.spec.md` |
| **Stage 3A** | **開發主力 (Lead Developer)** | Claude (`claude-opus-5-5`) | `.spec.md` | 代碼 + 測試 + `.impl.md` |
| **Stage 3B** | **協同開發 (Co-Developer)** | Gemini (`gemini-4-neon` high) | `.spec.md` | 代碼 + 測試 + 文件 + `.impl.md` |
| **Stage 4** | **驗收 (Reviewer，單一關)** | Codex (`gpt-6.2-sol`) | `.spec.md` + `.impl.md` + `git diff` | `docs/specs/<feature>.verify.md` |
| **加驗** | **紅隊（僅高風險）** | Daybreak (`gpt-daybreak-blue-latest`, effort high) | 僅高風險那段 diff | 寫入 `.verify.md` |

### Stage 3 分工（按風險與獨立性，不按前後端）

| 工作 | Claude（主力） | Gemini（協同） |
|------|----------------|----------------|
| 程式 | 核心商業邏輯、跨模組整合、DB schema 與 migration、權限／金流／併發（含 frontend 內的權限判斷） | frontend、契約清楚的低風險後端（CRUD、查詢 API、報表匯出、獨立背景工作） |
| 共用部分 | 型別、schema、路由、設定、套件清單 | 需要改時回報指揮 |
| 測試與文件 | 自己程式的測試、技術決定與限制 | 自己程式的測試、frontend 測試、README 與 API 使用說明 |

- 架構與開發即使同為 Claude，也用分開的對話。
- 同一檔案只有一人改；契約有問題時回報指揮，不自行改對方範圍。
- 契約清楚即可並行；合併後一起跑過測試才送驗。
- 純後端核心或很小的修改只派 Claude；Gemini 額度不足時全部由 Claude 做。
- Codex 額度用完時由 Grok 代驗。額外的複核或架構加審只在使用者點名時執行。

---

## 二、各階段標準產物契約 (Artifact Contracts)

### 1. Stage 2 — Claude 技術規格文檔 (`docs/specs/<feature>.spec.md`)

Claude 架構師在動手寫規格前，必須先讀取相關 Handler/Model/Component，嚴禁憑空假設介面格式。文檔必須包含：

```markdown
# [功能名稱] 技術規格文檔 (Swarm Stage 2 - Claude Spec)

- **作者**：Jacky (Architect: Claude Opus 5.5)
- **日期**：YYYY-MM-DD
- **狀態**：READY_FOR_DEV

## 1. 需求背景與範圍邊界
- **要做什麼（In-Scope）**：...
- **不做什麼（Out-of-Scope，防止過度設計）**：...

## 2. 資料庫與資料模型變更 (DB & Schema)
- 表結構 / 索引 / 遷移策略與向後相容性

## 3. API 契約與資料流 (API Contract)
- 端點路徑、Method、權限要求
- Request / Response 完整結構（必須符合專案統一成功回應包裝與分頁結構）
- 錯誤碼與異常處理分支

## 4. 檔案拆分與行數預估 (File Size Budget)
- 列出預計新增/修改的檔案，確保單檔不超過硬限制（Java ≤ 300, Go ≤ 400, Vue/TSX ≤ 200, TS/JS/Python ≤ 300）

## 5. 檔案分工與風險等級
- Claude 與 Gemini 各自可改的檔案清單（同一檔案只有一人改；共用型別、schema、路由、設定、套件清單歸 Claude）
- 風險等級：一般 / 高風險（權限、金流、schema migration、併發；判斷不準視為高風險）

## 6. 驗收標準 (Acceptance Criteria)
- [ ] AC-1：正常路徑行為與預期輸出
- [ ] AC-2：邊界條件（空值、重複提交、無權限、併發請求）
- [ ] AC-3：必須通過的自動化測試案例
```

---

### 2. Stage 3 — 實作與測試交接證據 (`docs/specs/<feature>.impl.md`)

開發者必須嚴格依 `.spec.md` 實作自己分到的檔案，不得留下任何 `TODO`、`MVP` 佔位符，不得竄改既有測試以掩蓋錯誤。完成後必須執行測試並產出：

```markdown
# [功能名稱] 實作交接證據 (Swarm Stage 3 - Implementation)

- **作者**：Jacky (Developers: Claude Opus 5.5 / Gemini 4 Neon)
- **對應規格**：`docs/specs/<feature>.spec.md`
- **狀態**：READY_FOR_QA

## 1. 變更檔案與行數檢查
| 檔案路徑 | 開發者 | 變更類型 (新增/修改) | 有效代碼行數 | 是否符合行數限制 |
|----------|--------|----------------------|--------------|------------------|

## 2. 規格對齊與實作說明
- 逐項對應 `.spec.md` 的 AC-1 ~ AC-N 說明實作方式

## 3. 編譯與測試執行證據 (Real Execution Output)
- 執行的具體指令（如 `go test ./...`、`mvn test`、`npm run typecheck`）
- 合併後的真實終端機輸出摘要（通過數、失敗數、耗時）

## 4. 驗收重點關注區
- 提醒驗收者特別檢查的複雜邏輯、交易邊界與高風險 diff 範圍
```

---

### 3. Stage 4 — 驗收報告 (`docs/specs/<feature>.verify.md`)

測試通過後由 Codex 單一關驗收，不改碼；高風險才另加紅隊。

```markdown
# [功能名稱] 驗收報告 (Swarm Stage 4)

- **總體結論**：`APPROVED` 或 `REJECTED`

## 驗收（Codex）
- **審查結論**：`PASS` / `FAIL`
- **架構與契約**：
  - [ ] 是否 100% 符合 `.spec.md` 的 API 契約與回應包裝？
  - [ ] 是否遵守檔案行數限制與防禦性編碼規範（無全域 ignore、無竄改測試、無 TODO）？
  - [ ] 多租戶隔離、權限校驗、資源釋放（DB/Stream/Lock）是否完整？
- **邊界反例**：
  - [ ] `null`、空陣列、超長字串、負數/零、時區跨日、浮點數精度
  - [ ] 重複點擊、併發寫入、鎖失效、Deadlock
  - [ ] N+1、大結果集未分頁/未流式匯出
  - [ ] 外部 API 超時或半途失敗時的 Transaction 與快取一致性
- **具體發現、反例與行號證據**：...

## 高風險加驗（僅權限、金流、schema migration、併發）
- **審查結論**：`PASS` / `FAIL` / `不適用`
```

---

## 三、退回重工與收斂規則 (Rework Loop)

1. 驗收或高風險加驗給出 `FAIL`，狀態即標記為 `REWORK_REQUIRED`。
2. 指揮者將帶有**具體檔案行號與觸發路徑**的阻塞問題派回給原開發者。
3. 原開發者做最小修復與補充測試，更新 `.impl.md`；**只複驗未通過的項目**，不整套重跑（最多重試 2 輪；需求本身矛盾時向使用者確認）。

---

## 四、本地工具鏈協作（CodeGraph / Ponytail / Headroom）

- **CodeGraph 優先（Stage 1–4 通用）**：若目標專案根目錄存在 `.codegraph/`，在撰寫 `.spec.md`、修改代碼或執行驗收前，優先透過 `codegraph_explore`（或 `codegraph explore "<symbol>"`）查詢呼叫鏈、依賴圖與影響範圍（Blast Radius），避免盲讀整庫或遺漏連動點；若無 `.codegraph/` 則跳過，不擅自建立索引。
- **Ponytail 精簡安全紀律（Stage 3 開發 / Stage 4 審查）**：只寫任務真正需要的最小乾淨實作（杜絕過度封裝與樣板碼），同時**絕不省略**輸入驗證、錯誤處理、安全性檢查與高風險邏輯測試。
- **Headroom 上下文壓縮（長任務傳輸層）**：Claude / Codex 透過本機 Headroom Proxy（如 `127.0.0.1:8787` / `headroom::gpt-6.2-sol`）自動壓縮長上下文與大檔讀取，搭配精簡結構化的 `.spec.md` / `.impl.md` / `.verify.md` 交接產物，降低 Token 消耗與爆窗風險。

---

## 規則溯源

```
> 📋 本回覆遵循：`swarm-workflow` - [Stage 1/2/3/4]
```
