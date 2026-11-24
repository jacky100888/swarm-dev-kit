---
name: swarm-workflow
description: Antigravity Swarm 四階段多模型協作工作流（Gemini 指揮協調 → Claude 技術規格 → Codex 核心開發 → Claude+Grok 雙軌交叉驗收）的標準產物契約與交接規範。
version: 2.0.0
---

# Antigravity Swarm 四階段多模型協作工作流

本技能定義多模型團隊（Gemini + Claude + Codex + Grok）在開發新功能、架構重構與複雜排障時的**職責邊界、交接產物格式（Artifact Contract）與雙軌驗收標準**。

---

## 一、四階段角色與模型配置

| 階段 | 角色 | 推薦模型 | 核心輸入 | 強制交接產物 (Artifact) |
|------|------|----------|----------|------------------------|
| **Stage 1** | **指揮協調者 (Coordinator)** | Google Gemini (`gemini-4-neon` / `gemini-3.8-flash`) | 使用者原始需求 | 任務拆解清單、看板派工指令 |
| **Stage 2** | **技術文檔與規格 (Architect)** | Claude (`claude-opus-5-5[1m]` / `claude-sonnet-5-5`) | 階段 1 派工 + 既有代碼庫 | `docs/specs/<feature>.spec.md` |
| **Stage 3** | **核心代碼開發 (Coder)** | Codex (`gpt-6.2-sol` / `gpt-6.2-astra`) | `docs/specs/<feature>.spec.md` | 代碼變更 + 單元測試 + `docs/specs/<feature>.impl.md` |
| **Stage 4A** | **架構與契約驗收 (Claude QA)** | Claude (`claude-opus-5-5`) | `.spec.md` + `.impl.md` + `git diff` | 架構契約審查結論（寫入 `docs/specs/<feature>.verify.md`） |
| **Stage 4B** | **紅隊邊界與漏洞驗收 (Grok QA)** | Grok (`grok-4.7`) | `.spec.md` + `.impl.md` + `git diff` | 極端邊界與併發漏洞審查結論（寫入 `docs/specs/<feature>.verify.md`） |

---

## 二、各階段標準產物契約 (Artifact Contracts)

### 1. Stage 2 — Claude 技術規格文檔 (`docs/specs/<feature>.spec.md`)

Claude 架構師在動手寫規格前，必須先讀取相關 Handler/Model/Component，嚴禁憑空假設介面格式。文檔必須包含：

```markdown
# [功能名稱] 技術規格文檔 (Swarm Stage 2 - Claude Spec)

- **作者**：Jacky (Architect: Claude Opus 5.5)
- **日期**：YYYY-MM-DD
- **狀態**：READY_FOR_CODEX

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

## 5. 驗收標準 (Acceptance Criteria)
- [ ] AC-1：正常路徑行為與預期輸出
- [ ] AC-2：邊界條件（空值、重複提交、無權限、併發請求）
- [ ] AC-3：必須通過的自動化測試案例
```

---

### 2. Stage 3 — Codex 實作與測試交接證據 (`docs/specs/<feature>.impl.md`)

Codex 工程師必須嚴格依 `.spec.md` 實作，不得留下任何 `TODO`、`MVP` 佔位符，不得竄改既有測試以掩蓋錯誤。完成後必須執行測試並產出：

```markdown
# [功能名稱] 實作交接證據 (Swarm Stage 3 - Codex Implementation)

- **作者**：Jacky (Coder: Codex GPT-6.2-Sol)
- **對應規格**：`docs/specs/<feature>.spec.md`
- **狀態**：READY_FOR_DUAL_QA

## 1. 變更檔案與行數檢查
| 檔案路徑 | 變更類型 (新增/修改) | 有效代碼行數 | 是否符合行數限制 |
|----------|----------------------|--------------|------------------|

## 2. 規格對齊與實作說明
- 逐項對應 `.spec.md` 的 AC-1 ~ AC-N 說明實作方式

## 3. 編譯與測試執行證據 (Real Execution Output)
- 執行的具體指令（如 `go test ./...`、`mvn test`、`npm run typecheck`）
- 真實終端機輸出摘要（通過數、失敗數、耗時）

## 4. 待雙軌驗收重點關注區
- 提醒 Claude 與 Grok 特別檢查的複雜邏輯或交易邊界
```

---

### 3. Stage 4 — Claude + Grok 雙軌交叉驗收報告 (`docs/specs/<feature>.verify.md`)

雙軌驗收必須由 **Claude（白盒架構/契約軌）** 與 **Grok（紅隊邊界/攻擊軌）** 獨立審查：

```markdown
# [功能名稱] 雙軌交叉驗收報告 (Swarm Stage 4 - Dual-Track QA)

- **總體結論**：`APPROVED`（雙軌皆通過） 或 `REJECTED`（任一軌退回重工）

## Track A：Claude 架構與契約審查 (Architecture & Contract)
- **審查結論**：`PASS` / `FAIL`
- **檢查項**：
  - [ ] 是否 100% 符合 `.spec.md` 的 API 契約與回應包裝？
  - [ ] 是否遵守檔案行數限制與防禦性編碼規範（無全域 ignore、無竄改測試、無 TODO）？
  - [ ] 多租戶隔離、權限校驗、資源釋放（DB/Stream/Lock）是否完整？
- **具體發現與行號證據**：...

## Track B：Grok 紅隊邊界與漏洞壓力審查 (Adversarial & Edge Cases)
- **審查結論**：`PASS` / `FAIL`
- **紅隊挑錯維度**：
  - [ ] **極端輸入與型別邊界**：`null`、空陣列、超長字串、負數/零、時區跨日、浮點數精度溢位
  - [ ] **併發與競態條件 (Race Condition)**：重複點擊、併發扣減/寫入、分佈式鎖失效、Deadlock
  - [ ] **效能與資源耗盡**：迴圈內查 DB (N+1)、大結果集未分頁/未流式匯出導致 OOM
  - [ ] **異常回滾一致性**：外部 API 超時或半途失敗時，DB Transaction 與快取是否髒寫？
- **反例構造與修復建議（附檔案行號）**：...
```

---

## 三、退回重工與收斂規則 (Rework Loop)

1. 只要 Track A (Claude) 或 Track B (Grok) 任一方給出 `FAIL`，狀態即標記為 `REWORK_REQUIRED`。
2. Gemini 指揮官將 `verify.md` 中帶有**具體檔案行號與觸發路徑**的阻塞問題派回給 Codex。
3. Codex 僅針對退回項目做最小修復與補充測試，更新 `.impl.md` 後重新觸發雙軌驗收（最多重試 2 輪；若屬需求本身矛盾則由 Gemini 指揮官向使用者確認）。

---

## 四、本地工具鏈協作（CodeGraph / Ponytail / Headroom）

- **CodeGraph 優先（Stage 1–4 通用）**：若目標專案根目錄存在 `.codegraph/`，在撰寫 `.spec.md`、修改核心代碼或執行紅隊審查前，優先透過 `codegraph_explore`（或 `codegraph explore "<symbol>"`）查詢呼叫鏈、依賴圖與影響範圍（Blast Radius），避免盲讀整庫或遺漏連動點；若無 `.codegraph/` 則跳過，不擅自建立索引。
- **Ponytail 精簡安全紀律（Stage 3 開發 / Stage 4 審查）**：只寫任務真正需要的最小乾淨實作（杜絕過度封裝與樣板碼），同時**絕不省略**輸入驗證、錯誤處理、安全性檢查與高風險邏輯測試。
- **Headroom 上下文壓縮（長任務傳輸層）**：Claude / Codex 透過本機 Headroom Proxy（如 `127.0.0.1:8787` / `headroom::gpt-6.2-sol`）自動壓縮長上下文與大檔讀取，搭配精簡結構化的 `.spec.md` / `.impl.md` / `.verify.md` 交接產物，降低 Token 消耗與爆窗風險。

---

## 規則溯源

```
> 📋 本回覆遵循：`swarm-workflow` - [Stage 1/2/3/4]
```
