---
okf_version: "0.2"
type: Tool
title: TencentDB Agent Memory & Memory Hub Proxy
description: Shared memory layer and LLM request proxy that injects team memory, skills, and knowledge into agent prompts. Replaces ByteRover.
resource: https://collective.ultrains.ink
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
  at: 2026-10-13T17:15:00Z
sources:
  - id: tencent-memory-hub-live
    resource: https://collective.ultrains.ink
    title: Memory Hub Live Panel and API
    author: Tencent / Shared Memory Hub
    last_modified: 2026-10-13T17:15:00Z
  - id: tencent-memory-skill
    resource: .agents/skills/tencent-memory/SKILL.md
    title: Workspace TencentDB Agent Memory Skill & Proxy Utilities
    author: Aigent Team (PKMxKB)
    last_modified: 2026-10-13T17:15:00Z
---

# TencentDB Agent Memory

## What It Is

Memory Hub is a self-hosted LLM request proxy that **intercepts agent API calls and injects team memory, skills, and knowledge** before forwarding to the upstream LLM. It replaces ByteRover/`.remembyte/` as the durable shared memory layer for all Aigents in this vault.

- **Panel UI & Management API:** `https://collective.ultrains.ink` (Cloudflare Tunnel) | `http://100.93.157.43:8125` (Tailscale fallback)
- **LLM Proxy Host:** `https://aigent.ultrains.ink` (Cloudflare Tunnel) | `http://100.93.157.43:8096` (Tailscale fallback)
- **Instance ID:** `default`
- **Team:** `PKMxKB` (`team-zlamo42c9f`)
- **Default Agent:** `default-agent-CLAi` (`agt-zlortmcr52`)
- **User (CLAi):** `usr-zloreic8lp`
- **Credentials:** stored in `.env` at vault root (git-ignored)

## How It Works

Every AI agent (Antigravity, Claude Code, Codex, etc.) points its API base URL to the LLM proxy on **`https://aigent.ultrains.ink`** (or port **8096** via Tailscale) instead of the real LLM endpoint. On each request the proxy:

1. Identifies the session (via headers or interactive form)
2. Retrieves injected memory/skills for that team + agent
3. Prepends context to the system prompt
4. Forwards the enriched request to the upstream LLM

```
Agent → https://aigent.ultrains.ink/<agent-type>/default/v1/... → upstream LLM
```

## Proxy Endpoint Pattern

| Agent client | Base URL (Cloudflare Tunnel) | Base URL (Tailscale) |
|---|---|---|
| Antigravity / Claude Code | `https://aigent.ultrains.ink/claude-code/default` | `http://100.93.157.43:8096/claude-code/default` |
| Codex | `https://aigent.ultrains.ink/codex/default` | `http://100.93.157.43:8096/codex/default` |
| OpenClaw / Hermes | `https://aigent.ultrains.ink/openclaw/default` | `http://100.93.157.43:8096/openclaw/default` |
| CodeBuddy | `https://aigent.ultrains.ink/codebuddy/default` | `http://100.93.157.43:8096/codebuddy/default` |

## Aigent Usage Contract

When operating in this vault, all Aigents MUST:

1. **Use `.env` for credentials** — never hardcode the user key.
2. **Identify by team + agent headers** when bypassing the interactive form on the proxy:
   ```http
   Authorization: Bearer <TDAI_USER_KEY>
   x-team-id: team-zlamo42c9f
   x-agent-id: agt-zlortmcr52
   x-task-id: no-task
   x-conversation-id: <session-unique-id>
   ```
3. **Use the Dedicated Skill:** Load `.agents/skills/tencent-memory/SKILL.md` or run the CLI helper `.agents/skills/tencent-memory/scripts/tdai.py`.
4. **Do NOT use `.remembyte/` scripts** — ByteRover is fully deprecated and removed.
5. **Record durable architectural decisions via `.haft/`** — Memory Hub handles session context, prompt enrichment, and team skills; Haft handles binding DRRs and FPF governance.

## Operational Modes

### Mode 1: LLM Proxy (Prompt Injection)
Agents route standard LLM completions through `https://aigent.ultrains.ink/<agent-type>/default`. The proxy automatically:
- Resolves the agent and team identity from headers.
- Fetches active skills (e.g. `okf-knowledge-curator`, `code-review`, `api-docs`) and team memories.
- Prepends system instructions into the prompt.
- Forwards to the upstream LLM provider.

### Mode 2: Programmatic Memory & Skills Management
Agents query or contribute knowledge directly via the Management API on `https://collective.ultrains.ink`:

| Operation | Endpoint | CLI Helper Equivalent |
|---|---|---|
| **Verify Auth** | `POST /api/v1/meta/auth/verify` | `python3 .agents/skills/tencent-memory/scripts/tdai.py auth` |
| **Healmiy L3 Persona** | `POST /api/v1/chat-memory/layer` (L3) | `python3 .agents/skills/tencent-memory/scripts/tdai.py persona` |
| **Search Memories** | `POST /api/v1/chat-memory/search` | `python3 .agents/skills/tencent-memory/scripts/tdai.py search <query>` |
| **Fixed Memory Blocks**| `POST /api/v1/chat-memory/agent-fixed` | `python3 .agents/skills/tencent-memory/scripts/tdai.py fixed` |
| **List Teams** | `POST /api/v1/meta/team/list` | `python3 .agents/skills/tencent-memory/scripts/tdai.py teams` |
| **List Members** | `POST /api/v1/meta/team-member/list` | `python3 .agents/skills/tencent-memory/scripts/tdai.py members` |
| **List Agents** | `POST /api/v1/meta/agent/list` | `python3 .agents/skills/tencent-memory/scripts/tdai.py agents` |
| **List Skills** | `POST /api/v1/skill/list` | `python3 .agents/skills/tencent-memory/scripts/tdai.py skills` |
| **Read Skill Prompt** | `POST /api/v1/skill/get` | `python3 .agents/skills/tencent-memory/scripts/tdai.py skill-get <skill_id>` |
| **Upload New Skill** | `POST /api/v1/skill/create` | `python3 .agents/skills/tencent-memory/scripts/tdai.py skill-create <name> <file>` |
| **Memory Overview** | `POST /api/v1/agent-overview/bootstrap` | `python3 .agents/skills/tencent-memory/scripts/tdai.py memories` |
| **Ingest Conversation** | `POST /api/v1/chat-memory/import` | `python3 .agents/skills/tencent-memory/scripts/tdai.py import <sess> <user> <asst>` |

### The 4-Layer Semantic Memory Pyramid (L0 to L3)

Shared agent memory is organized hierarchically to prevent token bloat while guaranteeing personal and project alignment:

| Layer | Architecture Tier | Storage & Purpose in PKMxKB |
|---|---|---|
| **L3** | **Persona / Core Memory** | Stores Healmiy's user profile, communication contract (direct/technical, no validation theater), Transformer Mandate, read-only PAT rules, and tax consulting directives. Automatically injected on agent boot. |
| **L2** | **Scenario / Projects** | Compartmentalizes pooled project experiences across `Passion` (Aigent Stack & Tech), `Profession` (Tax & Accounting), `Prime` (Islamic Knowledge), and `Public` (Systems). |
| **L1** | **Atomic Facts & Rules** | Granular facts and operational constraints extracted for precision recall without scanning chat transcripts. |
| **L0** | **Conversation Dialogue** | Raw conversation turns and execution session logs imported into the cluster for continuous audit and distillation. |


## Health Checks

```bash
# 1. Panel Web UI & API reachability (Cloudflare Tunnel)
curl -s -i https://collective.ultrains.ink/ | head -10

# 2. Authenticate with live User Key
curl -s -X POST https://collective.ultrains.ink/api/v1/meta/auth/verify \
  -H "Content-Type: application/json" \
  -H "x-tdai-service-id: default" \
  -d "{\"user_key\":\"$TDAI_USER_KEY\"}"
# Expect: {"code":0,"data":{"valid":true,"user":{"username":"CLAi",...}}}

# 3. LLM Proxy Host reachability
curl -s -i https://aigent.ultrains.ink/ | head -10
```

## Setup Reference & Tooling

- **Workspace Skill:** `.agents/skills/tencent-memory/SKILL.md`
- **CLI Utility:** `.agents/skills/tencent-memory/scripts/tdai.py`
- **Client Configuration Script:** `.agents/skills/tencent-memory/scripts/setup-proxy.sh`
- **Asset Importer (Offline Sessions):** `.agents/skills/tencent-memory/scripts/asset-import.ts`

### Client Agent Configuration Reference

The 7 supported client environments and their corresponding configuration files:

| Client Agent | Config File Path | Protocol | Key Configuration Requirement |
|---|---|---|---|
| **Claude Code** | `~/.claude/settings.json` | Anthropic Messages | Set `ANTHROPIC_BASE_URL` in `env` to proxy URL |
| **CodeBuddy** | `~/.codebuddy/models.json` | OpenAI Chat | Append model entry to `models` array with proxy URL |
| **Codex** | `~/.codex/config.toml` | OpenAI Responses | TOML configuration, requires `wire_api = "responses"` |
| **WorkBuddy** | `~/.workbuddy/models.json` | OpenAI Chat / Responses | Top-level array entry with proxy endpoint |
| **dsh (DeepSeek)** | `~/.dsh/settings.yaml` + `~/.dsh/.credentials.yaml` | OpenAI Chat (no `/v1`) | Base URL without `/v1`, requires `chmod 700/600` |
| **Hermes** | `~/.hermes/config.yaml` | OpenAI Chat | Pre-select headers (`x-team-id`, `x-agent-id`, `x-task-id`) |
| **OpenClaw** | `~/.openclaw/openclaw.json` | OpenAI Chat | Pre-select headers + enable `allowPrivateNetwork` |

### Automated Client Setup Command

To configure any agent non-interactively using the bundled setup script:

```bash
bash .agents/skills/tencent-memory/scripts/setup-proxy.sh --non-interactive \
  --proxy-host "https://aigent.ultrains.ink" \
  --instance-id "default" \
  --user-key "$TDAI_USER_KEY" \
  --agent "<agent-name>" \
  --model "<upstream-model-id>"
```

### Guidance for Other Aigents (CLAi, AiPhone Team, etc.)

When joining this workspace, newly spawned or external Aigents must:
1. Source `.env` for credentials (`TDAI_USER_KEY`, `TDAI_TEAM_ID`, `TDAI_AGENT_ID`).
2. Route LLM inference through `https://aigent.ultrains.ink` (Cloudflare Tunnel) or `http://100.93.157.43:8096` (Tailscale).
3. Query or update shared knowledge and skills via `https://collective.ultrains.ink` using `tdai.py`.
4. Ensure default team ID is `team-zlamo42c9f` (`PKMxKB`) and agent ID is `agt-zlortmcr52` (`default-agent-CLAi`) or their designated agent ID.

## Migration from ByteRover

| Feature | ByteRover (Deprecated) | TencentDB Memory Hub (Active) |
|---|---|---|
| **Storage Engine** | Local `.remembyte/` context-tree | Centralized Memory Hub service |
| **Injection Mechanism** | Agent runs Node.js scripts to read files | Proxy automatically injects into LLM prompt |
| **Agent Skill** | `.agents/skills/byterover` (removed) | `.agents/skills/tencent-memory` |
| **Governance Boundary** | Mixed into memory files | Strict separation: `.haft/` for decisions, Memory Hub for team context |
