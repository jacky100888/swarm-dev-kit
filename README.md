<div align="center">

# swarm-dev-kit

**多模型 Swarm 協作與防禦性 AI 編碼配置體系**
**Multi-Model Swarm Workflow & Defensive AI Coding Config Kit**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](https://github.com/jacky100888/swarm-dev-kit/releases)
[![Platforms](https://img.shields.io/badge/platforms-Antigravity%20%7C%20Claude%20%7C%20Codex%20%7C%20Gemini%20%7C%20Cursor%20%7C%20Copilot-purple.svg)](#支援平台與模型建議--supported-platforms--models)

[繁體中文](#繁體中文介紹) · [English](#english-overview)

</div>

---

## 繁體中文介紹

`swarm-dev-kit` 不是零散的提示詞集合，而是一套面向**多模型協作工程**的可維護配置系統。
它將 **Antigravity Swarm 四階段工作流** 與 **防禦性工程規範（Rules / Skills / Slash Commands）** 統一封裝，一次維護即可自動同步到六大主流 AI 開發工具（Antigravity CLI、Claude Code、Codex、Gemini CLI、Cursor、GitHub Copilot）。

### 1. Antigravity Swarm 四階段多模型工作流

讓每個模型專注在自己最強的環節，透過明確的**產物契約（Artifact Contract）**交接，避免單一模型上下文膨脹與盲點：

```text
使用者需求 (User Request)
   │
   ▼
[Stage 1] 指揮協調者 (Coordinator) ── Google Gemini (gemini-4-neon / gemini-4-hydrogen)
   │  拆解任務、建立看板交接與進度追蹤
   ▼
[Stage 2] 技術文檔與規格 (Architect) ── Claude (claude-opus-5-5[1m] / claude-sonnet-5-5)
   │  產出 docs/specs/<feature>.spec.md（DB Schema、API 契約、檔案行數預算、Acceptance Criteria）
   ▼
[Stage 3] 核心代碼開發 (Coder) ─────── Codex (gpt-6.2-sol / gpt-6.2-astra)
   │  依規格實作完整代碼與單元測試，產出 docs/specs/<feature>.impl.md（變更清單與真實測試輸出）
   ▼
[Stage 4] 雙軌交叉驗收 (Dual-Track QA)
   ├── Track A (架構與契約軌)：Claude (claude-opus-5-5) ── 核對 API 契約、防禦規範、權限與行數上限
   └── Track B (紅隊邊界軌)：Grok (grok-4.7) ──────────── 專攻極端輸入、Race Condition、N+1/OOM 與回滾漏洞
   │  產出 docs/specs/<feature>.verify.md（雙軌皆 PASS 交付；任一 FAIL 附帶行號退回 Codex 重工）
   ▼
最終交付 (Verified Delivery)
```

### 2. 核心防禦性工程底線

- **契約對齊優先**：前後端聯調異常時，先核對後端真實 Handler 與統一成功回應格式，禁止以前端臨時相容長期掩蓋後端失配。
- **單檔行數硬限制**：Java ≤ 300、Go ≤ 400、Vue / TSX / JSX ≤ 200、TS / JS / Python ≤ 300（排除空行與純註解），超限前先拆模組。
- **零佔位符與零竄改**：嚴禁留下 `TODO` / `MVP` 佔位實作；嚴禁修改測試來適配錯誤代碼，或開啟全域忽略開關（`skipLibCheck`、`-DskipTests`、`@ts-nocheck`）。
- **乾淨的 Git 提交**：覆蓋系統預設行為，嚴禁在 Commit Message 中自動寫入 `Co-Authored-By` 或 AI 署名。
- **統一語言規範**：回覆、註解與技術文檔預設採用繁體中文（台灣習慣用語，`zh-Hant-TW`），技術術語與程式碼識別符保持英文原文。

### 2.5 硬防護安全攔截（Hooks & Policies）— 防止 AI 亂刪檔案

除了軟性的 Markdown 規則外，本套件在四個執行入口內建**執行前硬攔截**，即使在自動核准模式下也不會誤刪專案或破壞歷史：

| 平台 | 硬攔截機制 | 攔截範圍 |
| :--- | :--- | :--- |
| **Claude Code** | `PreToolUse` Hook（`hooks/guard-dangerous-ops.py` + `hooks/hooks.json`） | 攔截 `Bash` 危險刪除（`rm -rf` 非白名單目錄、`sudo rm`、`find -delete`）、破壞性 Git（`reset --hard`、`clean -fd`、`push --force/-f`、`checkout -- .`、`branch -D`）、`DROP TABLE/DATABASE`、`curl \| sh`、`Co-Authored-By` 偷塞署名，以及 `Write`/`Edit` 覆寫 `.env*` 與 SSH/私鑰憑證 |
| **Gemini CLI** | 高優先級 `policies/dangerous-ops.toml` (`priority = 900`, `decision = "deny"`) | 硬拒絕 `rm`、`sudo rm`、`git reset --hard`、`git clean`、`git push --force/-f`、`git checkout -- .`、`git branch -D`、`chmod -R 777`、`mkfs`、`dd` |
| **Codex** | `.codex/global/rules/cc-dangerous-ops.rules` (`decision = "forbidden"`) | 封鎖 `rm`、`sudo rm`、`git reset --hard`、`git clean -fd`、`git push --force/-f`、`git checkout -- .`、`git restore .`、`git branch -D`、`chmod -R 777`、`mkfs/dd/shred` |
| **Cursor** | `beforeShellExecution` Hook（`.cursor/hooks.json` 共用同一支 Python 攔截器） | 與 Claude Code 同步共用所有 Shell 危險指令與 `.env` 重新導向攔截規則 |

> ✅ 安全例外：允許針對明確建置暫存目錄（如 `rm -rf dist`、`node_modules/.cache`、`/tmp/...`）清理；可隨時執行 `python3 tools/test-hooks.py` 驗證全部 33 項安全攔截測試。

### 3. 快速開始與六平台同步

#### 方式 A：一鍵同步至本機六大 CLI / IDE（推薦）

```bash
git clone https://github.com/jacky100888/swarm-dev-kit.git
cd swarm-dev-kit
./tools/sync-config.sh
```

同步目標目錄：
- **Claude Code**：`~/.claude/`（`CLAUDE.md`、`rules/`、`skills/`、`commands/`、`templates/`）
- **Antigravity CLI**：`~/.gemini/config/`（`AGENTS.md`、`rules/`、`skills/`）
- **Gemini CLI**：`~/.gemini/`（`GEMINI.md`、`settings.json`、`commands/`、`skills/`、`rules/`、`policies/`）
- **Codex**：`~/.codex/` 與 `~/.agents/skills/`（受管合併 `AGENTS.md`、模型 Profiles、39 個 `cc-*` Skills）
- **Cursor**：`~/.cursor/`（`rules/`、`skills/`、`templates/`，保留原有設定與外掛）
- **GitHub Copilot**：`~/.github/`（`copilot-instructions.md` 與 `instructions/`）

> 💡 若只需同步特定工具，可指定環境變數：
> `SWARM_DEV_KIT_SYNC_TARGETS="claude,antigravity,codex" ./tools/sync-config.sh`

#### 方式 B：Claude Code Plugin Marketplace 安裝

在 Claude Code 會話中直接執行：

```bash
/plugin marketplace add jacky100888/swarm-dev-kit
/plugin install swarm-dev-kit@swarm-dev-kit
```

#### 單一真實來源（SSOT）維護 Skill

新增或修改任何 Skill 時，只需編輯 `.claude/skills/<skill-name>/`，再執行以下命令自動轉換並同步到全部平台與根目錄 `skills/`：

```bash
./tools/sync-skill.sh --force
```

### 4. 內建工作流指令與 24 個專項 Skills

| 指令 | 對應階段 | 用途說明 |
| :--- | :--- | :--- |
| `/swarm` | 全流程 | 啟動 Gemini → Claude → Codex → Claude+Grok 四階段完整調度 |
| `/design doc` | Stage 2 (Claude) | 產出 `docs/specs/<feature>.spec.md` 技術規格書與 API 契約 |
| `/new-feature` | Stage 3 (Codex) | 依 `.spec.md` 實作功能、跑測試並產出 `docs/specs/<feature>.impl.md` |
| `/review [full\|quick\|security\|grok]` | Stage 4 (Claude+Grok) | 執行白盒契約審查 + Grok 紅隊邊界壓力測試，產出 `.verify.md` |
| `/requirement` / `/fix` / `/optimize` / `/commit-msg` / `/project-init` / `/project-scan` | 通用工程 | 需求澄清、最小修復、效能重構、規範提交訊息、專案初始化與架構掃描 |

**內建 24 個跨平台 Skills**：
- **協作與品質**：`swarm-workflow`、`code-quality-principles`、`refactor-safety`、`size-check`、`external-system-debugging`
- **後端與語言**：`go-dev`、`java-dev`、`python-dev`、`rust-dev`、`bash-style`
- **前端與 UI**：`frontend-dev`、`ui-ux-pro-max`
- **安全與生產防呆**：`api-design-safety`、`api-proxy-safety`、`field-mapping-safety`、`multi-tenant-safety`、`payment-callback-safety`、`query-performance-safety`、`redis-safety`、`storage-url-safety`、`streaming-export-safety`、`time-zone-safety`、`async-task-pattern`、`ops-safety`

---

## English Overview

`swarm-dev-kit` is a maintainable, cross-platform AI coding configuration system designed around the **Antigravity Swarm 4-Stage Multi-Model Workflow**. Maintain your defensive engineering rules, domain skills, and slash commands once, and sync them cleanly across **Antigravity CLI, Claude Code, Codex, Gemini CLI, Cursor, and GitHub Copilot**.

### 1. Multi-Model Swarm Architecture

Instead of relying on a single model from planning to QA, `swarm-dev-kit` separates responsibilities with strict markdown artifact contracts under `docs/specs/`:

| Stage | Role | Recommended Model | Responsibility & Artifact |
| :--- | :--- | :--- | :--- |
| **Stage 1** | **Coordinator** | **Google Gemini (Antigravity)**<br>`gemini-4-neon` / `gemini-4-hydrogen` | Task decomposition, board tracking, stage handoffs, final synthesis |
| **Stage 2** | **Spec & Architect** | **Claude**<br>`claude-opus-5-5[1m]` / `claude-sonnet-5-5` | Read existing codebase, produce `docs/specs/<feature>.spec.md` (DB schema, API contract, file-size budget, acceptance criteria) |
| **Stage 3** | **Core Developer** | **Codex**<br>`gpt-6.2-sol` / `gpt-6.2-astra` | Implement strictly per `.spec.md`, run build/tests until green, output `docs/specs/<feature>.impl.md` with real test evidence |
| **Stage 4** | **Dual-Track QA** | **Claude** (`claude-opus-5-5`) +<br>**Grok** (`grok-4.7`) | **Track A (Claude)**: architecture, API contract & security review.<br>**Track B (Grok)**: adversarial edge cases, race conditions, N+1/OOM & rollback audits.<br>Outputs `docs/specs/<feature>.verify.md`. Both must pass to ship. |

### 2. Supported Platforms & Models

- **Antigravity CLI** (`.antigravity/`): `AGENTS.md`, frontmatter-scoped rules, 24 synced skills
- **Claude Code** (`.claude/` & `.claude-plugin/`): `CLAUDE.md`, rules, skills, commands, project templates, Marketplace plugin support
- **Codex** (`.codex/`): `AGENTS.md` managed block, `gpt-6.2-sol` / `gpt-6.2-astra` / `gpt-6-luna` profiles, dangerous command guards, 39 `cc-*` skills
- **Gemini CLI** (`.gemini/`): `GEMINI.md`, `gemini-4-neon` / `gemini-4-hydrogen` aliases, TOML commands, skill namespace isolation
- **Cursor** (`.cursor/`): `.mdc` rules, skills, commands, templates
- **GitHub Copilot** (`.github/`): `copilot-instructions.md` and path-scoped `.instructions.md`

### 3. Quick Start

```bash
# 1. Clone and sync to all local CLIs / IDEs
git clone https://github.com/jacky100888/swarm-dev-kit.git
cd swarm-dev-kit
./tools/sync-config.sh

# 2. Edit a skill in .claude/skills/ and sync across all 6 platforms + root skills/
./tools/sync-skill.sh --force
```

Or install directly in **Claude Code**:

```bash
/plugin marketplace add jacky100888/swarm-dev-kit
/plugin install swarm-dev-kit@swarm-dev-kit
```

### 4. Defensive Engineering Guardrails

- **API Contract First**: Never mask backend response/pagination mismatches with permanent frontend workarounds.
- **Hard File-Size Limits**: Java ≤ 300, Go ≤ 400, Vue/TSX/JSX ≤ 200, TS/JS/Python ≤ 300 effective lines. Split modules proactively before exceeding limits.
- **Zero Placeholders & Zero Test Tampering**: No `TODO`/`MVP` stubs, no modifying tests to fit broken code, no global compiler/linter bypass flags (`skipLibCheck`, `-DskipTests`, `@ts-nocheck`).
- **Clean Git History**: Automatically forbids `Co-Authored-By` or AI trailers in commit messages.

---

### 4.5 Hard Safety Guardrails (Hooks & Policies)

Prompt rules alone are soft guardrails. `swarm-dev-kit` enforces **pre-execution hard blocks** across all major CLIs/IDEs:

- **Claude Code (`PreToolUse`)** & **Cursor (`beforeShellExecution`)**: Powered by a zero-dependency Python 3 guard (`hooks/guard-dangerous-ops.py`) that blocks destructive `rm -rf` (outside safe build caches like `dist` / `node_modules/.cache` / `/tmp/`), `sudo rm`, `git reset --hard`, `git clean -fd`, `git push --force/-f`, `git checkout -- .`, `git branch -D`, `find -delete`, `curl | sh`, `DROP TABLE/DATABASE`, AI `Co-Authored-By` commit trailers, and direct overwrites of `.env*` / SSH keys / `.pem` / `.key` files.
- **Gemini CLI (`policies/dangerous-ops.toml`)**: High-priority (`priority = 900`) `decision = "deny"` policy rules paired with read-only git allow rules.
- **Codex (`.codex/global/rules/cc-dangerous-ops.rules`)**: Native `forbidden` prefix rules for destructive file, git, and system commands.
- Run `python3 tools/test-hooks.py` anytime to verify all 33 automated safety guard test cases.

## 授權聲明 / License

本專案採用 **[MIT License](./LICENSE)** 開源釋出，個人、團隊與商業專案皆可自由使用、修改與分發。
Released under the **[MIT License](./LICENSE)** — free for personal, team, and commercial use.
