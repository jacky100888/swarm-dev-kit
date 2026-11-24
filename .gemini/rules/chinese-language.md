<skill_rules>
## 中文語言規則（繁體中文）

> CRITICAL: You MUST respond in Traditional Chinese (zh-Hant-TW) at ALL times unless explicitly requested otherwise.
> 更具體規則（專案既有英文規範、使用者明確要求）優先級更高。

### 覆蓋順序
使用者明確要求英文 → 專案既有英文規範 → 預設繁體中文（台灣習慣用語，本規則）

### 規則
1. **回覆語言**：回覆、解釋、建議一律使用繁體中文（zh-Hant-TW）。技術術語保持英文原文（GORM、context.Context）。
2. **程式碼註解**：新增註解、文檔註解使用繁體中文。不翻譯既有英文註解。
3. **Commit message**：subject/body 使用繁體中文。scope/type 前綴（feat:、fix:）保持英文。
4. **程式碼識別符（例外）**：變數/函式/型別名、資料庫欄位、JSON key、URL 路徑、列舉值保持英文。

### 判定速查

| 場景 | 語言 | 範例 |
|------|------|------|
| 回覆使用者 | 繁體中文 | "資料庫連線失敗，請檢查設定" |
| 程式碼註解 | 繁體中文 | // 根據使用者 ID 查詢訂單 |
| Commit subject | 繁體中文 | fix: 修復庫存超賣問題 |
| 技術術語 | 英文原文 | GORM, Gin, context.Context |
| 變數命名 | 英文 | userId, orderList, GetUser() |
| 錯誤日誌 | 保持原文 | log.Printf("connection refused: %v", err) |
</skill_rules>

<out_of_scope>
本規則不適用於使用者明確要求英文、技術術語、程式碼識別符、錯誤日誌原文。
</out_of_scope>
