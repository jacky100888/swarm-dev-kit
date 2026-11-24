# Contributing to swarm-dev-kit

歡迎提交 Issue 與 Pull Request，一起完善多模型 Swarm 協作與跨平台 AI 編碼配置！
Contributions, issues, and pull requests are welcome to improve the multi-model Swarm workflow and cross-platform AI coding configurations.

## 開發與同步規範 / Development & Sync Guidelines

1. **單一真實來源 / Single Source of Truth**：
   修改或新增 Skill 時，請編輯 `.claude/skills/<skill-name>/`，然後執行：
   Edit or add skills in `.claude/skills/<skill-name>/`, then run:
   ```bash
   ./tools/sync-skill.sh --force
   ```
   以自動同步至 `skills/`、`.antigravity/skills/`、`.gemini/skills/`、`.cursor/skills/`、`.codex/skills/` 與 `.github/instructions/`。

2. **本機全域同步 / Local Global Sync**：
   執行 `./tools/sync-config.sh` 同步至本機各平台 CLI/IDE 設定目錄。

3. **授權條款 / License**：
   所有貢獻皆以本專案之 [MIT License](./LICENSE) 釋出。

## 回報問題 / Issues

- GitHub Issues: <https://github.com/jacky100888/swarm-dev-kit/issues>
