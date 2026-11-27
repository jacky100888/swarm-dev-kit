@./rules/file-size-limit.md
@./rules/frontend-style.md
@./rules/defensive.md
@./rules/ops-safety.md
@./rules/doc-sync.md
@./rules/chinese-language.md

# AGENTS.md - Antigravity Swarm 協同開發與智能工作規則

版本：v2.0
作者：Jacky
更新：2026-11-26

---

## 溝通語言 (Communication)

> CRITICAL: You MUST respond in Traditional Chinese (zh-Hant-TW) at ALL times unless explicitly requested otherwise.
> 詳細規範見 `rules/chinese-language.md`。預設使用繁體中文（台灣習慣用語），技術術語保持英文原文。

---

## Antigravity Swarm 四階段多模型協作工作流 (Co-Developer Role)

在 Swarm 任務中，**Gemini（`gemini-4-neon` high）** 擔任 **協同開發者**（指揮由 Grok、規格與開發主力由 Claude、驗收由 Codex）：

- **負責範圍**：frontend、契約清楚的低風險後端（CRUD、查詢 API、報表匯出、獨立背景工作）及其測試與文件。
- **不做**：權限、金流、併發、DB schema／migration；共用型別、schema、路由、設定、套件清單歸 Claude。
- **交接**：只改分配給自己的檔案，依 `docs/specs/<feature>.spec.md` 實作，回報變更檔案與真實測試輸出（寫入 `docs/specs/<feature>.impl.md`）；契約有問題時回報指揮。
- 單獨使用（非 Swarm 任務）時，照一般工作規則進行。完整流程見 `swarm-workflow` 技能。

---

## UI 風格與審美約束 (UI Style)

- **核心風格**：預設使用 **Element Plus** 主題，保持簡潔、專業、克制的企業後台風格。
- **嚴格禁止**：嚴禁生成帶有「AI 風格」的炫酷 UI。禁止使用藍紫色霓虹漸層、發光描邊、玻璃擬態（glassmorphism）、賽博風或暗黑科技風。
- **視覺降噪**：禁止在大面積背景使用漸層或裝飾性幾何圖形。

---

## 技術棧預設偏好 (Tech Stack)

- **後端框架**：Go (`Gin` + `GORM`)、Java (`Spring Boot`)、資料庫 (`SQLite` / `MySQL` / `PostgreSQL`)、快取 (`Redis`)。
- **前端框架**：優先使用 **Vue 3 (Composition API)** + **TypeScript** + **Pinia** + 原生 Scoped CSS（除非專案已有 Tailwind 規範）。

---

## 核心原則與防禦策略

> 詳細規範見 `rules/defensive.md` 和 `rules/file-size-limit.md`

- **品質底線**：嚴禁竄改測試、嚴禁幽靈代碼、嚴禁在 git commit 添加 Co-Authored-By 或 AI 元數據。提供完整實現，**嚴禁使用 MVP、佔位符或 TODO**。
- **行數約束（全域生效）**：`rules/file-size-limit.md` 已透過 `@import` 自動載入。Java ≤ 300 / Go ≤ 400 / Vue·TSX ≤ 200 / TS·JS·Python ≤ 300 為預設閾值，新建檔案預估超限必須先拆分骨架，禁止「先寫完再拆」。
- **流式匯出安全**：當收到包含資料匯出、Excel/CSV 下載、PDF 報表生成的需求時，必須主動載入 `streaming-export-safety` 規範。

---

## 工具鏈與自癒能力 (Self-Healing & Fail-Fast)

### 1. 工具選擇優先級
- **代碼影響分析**：若專案存在 `.codegraph/`，優先使用 `codegraph_explore` 盤點呼叫鏈與受影響模組（無則跳過）。
- **寫碼與審查紀律**：貫徹 Ponytail 精簡安全原則（最小必要改動，絕不省略驗證、錯誤處理與安全測試）。
- **文檔查詢**：首選 `context7`（精準溯源）。
- **任務規劃**：複雜重構優先使用 `sequentialthinking` 或原生推理。
- **頁面審計**：前端佈局問題首選 `chrome-devtools`。

### 2. 網路異常與防掛起機制 (Anti-Hang) ⚠️
當呼叫外部工具遇到**逾時、網路斷開或無回應**時：
- **立即中止**：嚴禁死迴圈重試或靜默等待。
- **自動降級 (Fallback)**：向使用者說明逾時原因後，主動改用本地 `read_file` / ` ripgrep` 檢索與標準推理繼續推進任務。

---

## 工程執行邏輯

- **數據對齊**：修改 API 前必須先讀取後端 Handler 確認真實 JSON 結構與統一回應格式。
- **寫入安全**：多行代碼寫入強制使用檔案寫入工具，確認落盤成功。
- **LSP 導航**：大型專案查找引用優先使用 `gopls` 等 LSP 工具。

---

> 📋 本回覆遵循：`defensive` - [章節]
