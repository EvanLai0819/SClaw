# Architecture

## Overview

SClaw is a small asyncio service that routes Web UI messages to an agent
loop, executes tools, stores memory in SQLite, and exposes a local dashboard.

## Runtime Flow

1. A channel (Web UI or console) receives a message.
2. Gateway routes the message to the agent.
3. Agent builds context, selects tools, calls the LLM, and executes tools.
4. Memory store saves history and long-term facts.
5. Audit log records every action.
6. Scheduler can send proactive messages via the gateway.

## Modules

- `sclaw/core`: agent loop, context builder, config, LLM client, logging.
- `sclaw/tools`: core tools (shell, files, web, memory, spawn) and registry.
- `sclaw/skills`: built-in skills loaded from disk.
- `sclaw/security`: sandbox, file guard, prompt guard, audit, budget.
- `sclaw/memory`: SQLite store for history and memories.
- `sclaw/channels`: gateway, Web UI, console.
- `sclaw/cron`: scheduler for recurring jobs.
- `sclaw/dashboard`: local aiohttp server and single-file UI.

## Data Stores

- SQLite at `~/.sclaw/data/sclaw.db` for history, memories, cron, audit.

## Dependencies

- aiohttp
- click
- pydantic
- sqlite3 (stdlib)
- html2text
- croniter

## Security Boundaries

- FileGuard restricts file access to `~/.sclaw/workspace`.
- ShellSandbox blocks dangerous commands and confirms destructive ones.
- PromptGuard sanitizes tool output and detects injection patterns.
- Dashboard and Web UI bind to localhost only.
