---
description: 雙軌交叉代碼驗收（Swarm Stage 4 - Claude 架構契約審查 + Grok 紅隊邊界漏洞審查）
allowed-tools: Bash(git diff:*), Bash(git status:*), Bash(git log:*), Bash(git show:*), Bash(git rev-parse:*), Read, Glob, Grep
argument-hint: "[full|quick|security|grok] [commit-hash] 預設 full 執行 Claude+Grok 雙軌全量驗收"
---

> **Swarm Stage 4（Claude + Grok 雙軌交叉驗收）**：對照 Stage 2 技術規格（`.spec.md`）與 Stage 3 代碼變更（`git diff` / `.impl.md`），執行白盒契約審查（Claude 軌）與紅隊邊界漏洞審查（Grok 軌）。

參數值：「$ARGUMENTS」

---

## 審查模式

- `/review` 或 `/review full` → **Swarm 雙軌全量驗收**（同時輸出 Track A Claude 架構契約審查 + Track B Grok 紅隊邊界漏洞審查）
- `/review quick` → 快速 diff 與阻斷性問題結論
- `/review security` → 安全與權限邊界專項審查
- `/review grok` → 專注執行 Track B（Grok 紅隊極端邊界、併發競爭、反例壓力測試）

---

## 雙軌交叉驗收檢查清單

### Track A：Claude 架構與契約審查 (Architecture & API Contract)
1. **規格與契約對齊**：是否 100% 符合 `docs/specs/<feature>.spec.md` 的 API 路徑、Request/Response 結構、統一回應包裝與分頁格式？有無用前端臨時相容掩蓋後端格式失配？
2. **防禦性規範與行數限制**：
   - 單檔有效行數是否控制在硬限制內（Java ≤ 300 / Go ≤ 400 / Vue·TSX ≤ 200 / TS·JS·Python ≤ 300）？
   - 是否存在 `TODO` / `MVP` 佔位符、被竄改的測試、或全域放行開關（`skipLibCheck`、`-DskipTests`）？
3. **安全與資源管理**：多租戶 `tenant_id` 隔離、權限校驗、SQL 注入防護、DB Connection / Stream / Context 釋放是否完整？

### Track B：Grok 紅隊邊界與漏洞壓力審查 (Adversarial & Edge-Case QA)
1. **極端輸入與型別邊界**：`nil`/`null`/`undefined`、空陣列 `[]`、超長字串、負數與 `0`、跨時區日期切點、浮點數金額精度損失。
2. **併發與競態條件 (Race Condition)**：使用者連點重複提交（冪等性缺失）、併發扣減庫存/餘額、Goroutine/Thread 共享狀態未加鎖、分佈式鎖過期或死鎖。
3. **效能與資源耗盡**：迴圈內查 DB / 呼叫 RPC (N+1 問題)、未分頁全表載入導致 OOM、大檔案匯出未走流式處理。
4. **半途失敗與髒資料**：外部第三方 API 超時或失敗時，本地 DB Transaction 與 Redis 快取是否不一致？

---

## 輸出格式（可同步寫入 `docs/specs/<feature>.verify.md`）

```markdown
# 雙軌交叉驗收報告 (Swarm Stage 4)

- **總體結論**：`APPROVED`（雙軌皆通過） 或 `REJECTED`（需退回 Codex 重工）

## 1. Track A — Claude 架構與契約審查結論 (`PASS` / `FAIL`)
- [列出通過項與違規項，違規項必須附帶 `檔案路徑:行號` 與修復要求]

## 2. Track B — Grok 紅隊邊界與漏洞審查結論 (`PASS` / `FAIL`)
- [列出構造的反例觸發路徑、`檔案路徑:行號`、風險等級 (P0/P1/P2) 與最小修復代碼建議]

## 3. 退回 Codex 重工清單（若 REJECTED）
1. `[P0] path/to/file:L123` — 問題描述與具體修正指令
```
