---
okf_version: "0.2"
type: Tool
title: TencentDB Agent Memory & Memory Hub Proxy
description: Shared memory layer and LLM request proxy that injects team memory, skills, and knowledge into agent prompts. Replaces ByteRover.
resource: http://100.93.157.43:8125
aliases:
  - Memory Hub
  - Tencent Memory Proxy
tags:
  - aigent
  - memory
  - infrastructure
  - proxy
  - tencentdb
status: stable
generated:
  by: reference_agent/antigravity
  at: 2026-10-13T14:40:00Z
sources:
  - id: tencent-memory-hub-live
    resource: http://100.93.157.43:8125
    title: Memory Hub Live Panel and API
    author: Tencent / Shared Memory Hub
    last_modified: 2026-10-13T14:40:00Z
  - id: tencent-agent-shared-memory-repo
    resource: .tmp/Tencent-agent-shared-memory/README.md
    title: Tencent Agent Shared Memory Integration Documentation
    author: upstream-repo
    last_modified: 2026-10-13T14:26:00Z
---

# TencentDB Agent Memory

## What It Is

Memory Hub is a self-hosted LLM request proxy that **intercepts agent API calls and injects team memory, skills, and knowledge** before forwarding to the upstream LLM. It replaces ByteRover/`.remembyte/` as the durable shared memory layer for all Aigents in this vault.

- **Panel UI:** `http://100.93.157.43:8125` (Tailscale)
- **Instance ID:** `default`
- **Team:** `PKMxKB` (`team-zlamo42c9f`)
- **Default Agent:** `default-agent-CLAi` (`agt-zlortmcr52`)
- **User (CLAi):** `usr-zloreic8lp`
- **Credentials:** stored in `.env` at vault root (git-ignored)

## How It Works

Every AI agent (Antigravity, Claude Code, Codex, etc.) points its API base URL to the proxy instead of the real LLM endpoint. On each request the proxy:

1. Identifies the session (via headers or interactive form)
2. Retrieves injected memory/skills for that team + agent
3. Prepends context to the system prompt
4. Forwards the enriched request to the upstream LLM

```
Agent → http://100.93.157.43:8125/<agent-type>/default/v1/... → upstream LLM
```

## Proxy Endpoint Pattern

| Agent client | Base URL |
|---|---|
| Antigravity / Claude Code | `http://100.93.157.43:8125/claude-code/default` |
| Codex | `http://100.93.157.43:8125/codex/default` |
| OpenClaw / Hermes | `http://100.93.157.43:8125/openclaw/default` |
| CodeBuddy | `http://100.93.157.43:8125/codebuddy/default` |

## Aigent Usage Contract

When operating in this vault, all Aigents MUST:

1. **Use `.env` for credentials** — never hardcode the user key.
2. **Identify by team + agent headers** when bypassing the interactive form:
   ```
   x-team-id: team-zlamo42c9f
   x-agent-id: agt-zlortmcr52
   x-task-id: no-task
   x-conversation-id: <session-unique-id>
   Authorization: Bearer <TDAI_USER_KEY>
   ```
3. **Do NOT use `.remembyte/` scripts** — ByteRover is fully deprecated.
4. **Record durable decisions via `.haft/`** — Memory Hub handles session context; haft handles governance artifacts.

## Health Check

```bash
# Quick reachability test
curl http://100.93.157.43:8125/

# Auth verification
curl -s -X POST http://100.93.157.43:8125/api/v1/meta/auth/verify \
  -H "Content-Type: application/json" \
  -H "x-tdai-service-id: default" \
  -d '{"user_key":"<TDAI_USER_KEY>"}'
# Expect: {"code":0,"data":{"valid":true,...}}
```

## Setup Reference

Full agent setup skill: `.tmp/Tencent-agent-shared-memory/skills/setup-proxy/SKILL.md`
Full agent integration docs: `.tmp/Tencent-agent-shared-memory/README.md`

For new Aigent teams (CLAi, AiPhone, etc.) reading this doc:
- Load credentials from `.env`
- Use `http://100.93.157.43:8125` as proxy host
- Use `team-zlamo42c9f` and `agt-zlortmcr52` as default team/agent IDs
- Consult the setup skill to configure your specific client type

## Migration from ByteRover

| Was | Now |
|---|---|
| `.remembyte/` scripts | Not used — folder removed |
| `byterover` skill | Removed from `.agents/skills/` |
| `node scripts/query.mjs` | Memory injected automatically by proxy |
| `node scripts/record.mjs` | Store via Memory Hub panel or API |
| `AGENTS.md` byterover section | Replaced by this doc |
