#!/usr/bin/env python3
"""
swarm-dev-kit Cross-Platform Safety Guard Hook (Claude Code PreToolUse & Cursor beforeShellExecution)

Blocks destructive shell commands, sensitive file overwrites, and forbidden AI commit trailers
BEFORE execution so AI agents cannot accidentally delete files, wipe git history, or leak secrets.

Exit behavior:
  - Claude Code (PreToolUse): exit 2 with clear block reason on stderr (supported across all versions)
  - Cursor (beforeShellExecution): exit 0 with {"permission": "deny", "userMessage": ..., "agentMessage": ...}
  - Safe operations: exit 0 (Cursor receives {"permission": "allow"})
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

# Safe disposable build/cache directory basenames allowed for targeted `rm -rf <dir>`
SAFE_CLEAN_DIRS = {
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".output",
    ".turbo",
    ".vite",
    ".cache",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "target",
    "tmp",
}

# Sensitive file patterns blocked from Write / Edit / Shell overwrite
SENSITIVE_PATH_PATTERNS = [
    (re.compile(r"(^|/)\.env($|\.(?!example$|sample$|template$)[a-zA-Z0-9_.-]+)$"), "禁止直接覆寫環境變數機密檔（.env*）；僅允許修改 .env.example / .env.template"),
    (re.compile(r"(^|/)\.ssh/"), "禁止修改 SSH 金鑰與設定目錄 (~/.ssh/)"),
    (re.compile(r"(^|/)(id_rsa|id_ed25519|id_ecdsa)(\.pub)?$"), "禁止修改 SSH 私鑰或公鑰檔案"),
    (re.compile(r"\.(pem|key|p12|pfx|keystore)$", re.IGNORECASE), "禁止修改憑證或私鑰檔案 (*.pem / *.key)"),
    (re.compile(r"(^|/)(credentials\.json|secrets?\.(ya?ml|json|toml))$", re.IGNORECASE), "禁止修改憑證或機密設定檔"),
]

# Always-blocked destructive command patterns
DANGEROUS_COMMAND_RULES = [
    (re.compile(r"(^|[;&|\s])sudo\s+rm\b"), "禁止執行特權刪除指令 (sudo rm)"),
    (re.compile(r"(^|[;&|\s])git\s+reset\s+--hard\b"), "禁止執行 git reset --hard（會永久遺失未提交的變更）"),
    (re.compile(r"(^|[;&|\s])git\s+clean\s+-[a-zA-Z]*f"), "禁止執行 git clean -f/-fd（會永久刪除未追蹤檔案）"),
    (re.compile(r"(^|[;&|\s])git\s+push\s+.*(--force(?!-with-lease)|(?<!\S)-f(?!\S))"), "禁止執行 git push --force / -f（可能覆寫遠端提交歷史）"),
    (re.compile(r"(^|[;&|\s])git\s+checkout\s+(--\s+)?\.(\s|$|[;&|])"), "禁止執行 git checkout -- .（會丟棄整個工作區未暫存變更）"),
    (re.compile(r"(^|[;&|\s])git\s+restore\s+(--staged\s+)?\.(\s|$|[;&|])"), "禁止執行 git restore .（會丟棄整個工作區變更）"),
    (re.compile(r"(^|[;&|\s])git\s+branch\s+-D\b"), "禁止強制刪除分支 (git branch -D)，請改用安全刪除 -d 或由使用者手動確認"),
    (re.compile(r"(^|[;&|\s])(mkfs(\.[a-z0-9]+)?|wipefs|shred|shutdown|reboot|halt|poweroff)\b"), "禁止執行高危險系統層破壞或關機指令"),
    (re.compile(r"(^|[;&|\s])dd\s+.*\bof=/dev/"), "禁止使用 dd 寫入磁碟裝置"),
    (re.compile(r"(^|[;&|\s])chmod\s+(-R\s+)?777\b"), "禁止執行 chmod 777 開放全域權限"),
    (re.compile(r"(^|[;&|\s])find\s+.*\s-delete(\s|$|[;&|])"), "禁止執行 find -delete 批次刪除檔案"),
    (re.compile(r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba)?sh\b"), "禁止直接透過管道執行遠端未審核腳本 (curl/wget | sh)"),
    (re.compile(r"\b(DROP\s+(DATABASE|TABLE|SCHEMA)|TRUNCATE\s+TABLE)\b", re.IGNORECASE), "禁止直接執行破壞性資料庫指令 (DROP DATABASE/TABLE / TRUNCATE)"),
    (re.compile(r"(^|[;&|\s])git\s+commit\b.*Co-Authored-By:", re.IGNORECASE | re.DOTALL), "禁止在 git commit 中加入 Co-Authored-By 或 AI 署名（違反專案提交規範）"),
]


def is_safe_rm_target(target: str) -> bool:
    """Allow rm only on explicit disposable build/cache directories inside the repo or /tmp."""
    t = target.strip().strip("\"\x27")
    if not t:
        return False
    # Never allow wildcards, root, home, current/parent dir, or parent traversal
    if any(ch in t for ch in ("*", "?", "[", "]")):
        return False
    if t in {"/", ".", "./", "..", "../", "~", "$HOME", "${HOME}"}:
        return False
    if t.startswith(("/", "~", "$HOME", "${HOME}")) and not t.startswith("/tmp/"):
        return False
    if ".." in Path(t).parts:
        return False
    if t.startswith("/tmp/") and len(t) > len("/tmp/"):
        return True
    norm = t.rstrip("/")
    if norm in SAFE_CLEAN_DIRS:
        return True
    if norm.endswith("/.cache") or norm.endswith("/__pycache__") or norm == "node_modules/.cache":
        return True
    return False


def check_rm_command(command: str) -> str | None:
    """Inspect shell segments for dangerous rm invocations."""
    segments = re.split(r"&&|\|\||;|\n", command)
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        try:
            tokens = shlex.split(seg)
        except ValueError:
            # Fallback if unbalanced quotes
            tokens = seg.split()
        if not tokens:
            continue
        # Strip leading env assignments like FOO=1
        idx = 0
        while idx < len(tokens) and "=" in tokens[idx] and not tokens[idx].startswith("-"):
            idx += 1
        if idx >= len(tokens):
            continue
        if tokens[idx] == "sudo" and idx + 1 < len(tokens):
            idx += 1
        cmd = Path(tokens[idx]).name
        if cmd != "rm":
            continue

        flags = []
        targets = []
        parsing_flags = True
        for tok in tokens[idx + 1 :]:
            if parsing_flags and tok == "--":
                parsing_flags = False
                continue
            if parsing_flags and tok.startswith("-"):
                flags.append(tok)
            else:
                targets.append(tok)

        is_recursive_or_force = any(
            ("r" in f.lower() or "f" in f.lower() or f in ("--recursive", "--force"))
            for f in flags
        )
        if not targets:
            continue
        for target in targets:
            t_clean = target.strip()
            if t_clean in {"/", "/*", "~", "~/", "$HOME", ".", "./", "..", "../", "*"}:
                return f"禁止刪除關鍵路徑或萬用字元目標：rm {t_clean}"
            if is_recursive_or_force and not is_safe_rm_target(t_clean):
                return (
                    f"攔截到危險刪除指令：`rm` 目標 `{t_clean}` 不在安全暫存白名單內。"
                    "如需刪除專案檔案，請明確說明影響範圍並由使用者親自執行或確認。"
                )
    return None


def check_sensitive_path(file_path: str) -> str | None:
    if not file_path:
        return None
    norm = file_path.replace("\\", "/")
    for pattern, reason in SENSITIVE_PATH_PATTERNS:
        if pattern.search(norm):
            return f"{reason}（目標：{file_path}）"
    return None


def check_command(command: str) -> str | None:
    if not command or not command.strip():
        return None
    for pattern, reason in DANGEROUS_COMMAND_RULES:
        if pattern.search(command):
            return f"{reason}（指令：{command.strip()[:160]}）"

    rm_reason = check_rm_command(command)
    if rm_reason:
        return rm_reason

    # Block shell redirection overwriting .env or ssh keys
    redir_match = re.search(r">{1,2}\s*([\w./~$-]+)", command)
    if redir_match:
        target = redir_match.group(1)
        sens = check_sensitive_path(target)
        if sens:
            return f"禁止透過 Shell 重新導向覆寫機密檔：{sens}"

    return None


def main() -> int:
    mode = "auto"
    if "--cursor" in sys.argv:
        mode = "cursor"
    elif "--claude" in sys.argv:
        mode = "claude"

    raw = sys.stdin.read().strip()
    if not raw:
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    # Detect platform schema
    hook_event = payload.get("hook_event_name", "")
    is_cursor = (
        mode == "cursor"
        or hook_event == "beforeShellExecution"
        or ("command" in payload and "tool_name" not in payload)
    )

    reason = None
    if is_cursor:
        command = payload.get("command", "")
        reason = check_command(command)
        if reason:
            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "userMessage": f"🛡️ [swarm-dev-kit 安全攔截] {reason}",
                        "agentMessage": f"[BLOCKED by swarm-dev-kit safety guard] {reason}",
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        print(json.dumps({"permission": "allow"}))
        return 0

    # Claude Code PreToolUse schema
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if tool_name == "Bash":
        reason = check_command(str(tool_input.get("command", "")))
    elif tool_name in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        fp = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        reason = check_sensitive_path(fp)

    if reason:
        sys.stderr.write(f"🛡️ [swarm-dev-kit 安全攔截] {reason}\n")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
