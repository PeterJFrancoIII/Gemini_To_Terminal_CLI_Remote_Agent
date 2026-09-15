# Shared Cognitive Memory — Universal Agent Rules

> **Canonical reference:** `PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/docs/shared-cognitive-memory`
>
> Every Gemini, GPT/ChatGPT, Codex, Antigravity, or other authorized agent performing Shared Memory MCP work MUST consult and cite this reference.

## 1. Single Source of Truth
- Use only the canonical local `shared-cognitive-memory` MCP.
- Never create secondary memory stores, shadow databases, or alternate graph files.
- `InterAgent_Dialogue_Channel` is the sole inter-agent communication bus. Never create alternate dialogue channels.

## 2. Retrieval Protocol
- Normal retrieval: `search_nodes` → `open_nodes`.
- Query the relevant project/session before substantial work.
- Query `InterAgent_Dialogue_Channel` for relevant handoffs or coordination.
- `read_graph` is exceptional and permitted only for justified `debug` or `recovery` with an explicit reason.

## 3. Inter-Agent Communication
Every message to `InterAgent_Dialogue_Channel` must begin:

`[TIMESTAMP | SOURCE → DESTINATION | MSG:<unique-id> | SESSION:<canonical-session-id>]`

Use a specific agent name or `ALL` as destination. Keep payloads concise. Add `ACTION:` or `ACK:` only when needed.

## 4. Mandatory Provenance Citation
Whenever using another agent's findings, decisions, benchmarks, instructions, or state, cite the exact Shared Memory source:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

For MCP architecture/rules, also cite:

`Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

Never present peer-agent work as unsourced knowledge.

## 5. Writing State
Promote only durable, verified state: architecture decisions, empirical findings, configuration changes, completed milestones, blockers, and handoffs. Never store routine chatter, bulk logs, or tool dumps.

## 6. Supersession
Never silently contradict canonical state. When state changes, declare:

`SUPERSEDES: <prior entity/message/state>`

Preserve historical provenance.

## 7. Security
Never store passwords, API keys, bearer tokens, private keys, credential-bearing URLs, or unnecessary sensitive data. Store only abstract secret references when required.

## 8. MCP Integrity
- All Shared Memory reads/writes must pass through the hardened MCP.
- Never edit `memory.json` directly.
- Never restore or invoke `delete_*` tools or the retired stock 9-tool memory server.
- Never create, restore, or modify MCP network ingress unless explicitly authorized by the user and recorded as a canonical architecture decision in Shared Memory.

## 9. Session Isolation
Operate only within the exact canonical session ID. Never guess IDs or mix unrelated sessions.

## 10. Agent Lifecycle
Before substantial work: identify session → `search_nodes`/`open_nodes` → check relevant dialogue → cite peer provenance → execute/verify → write back only materially changed state → post concise handoff when needed.
