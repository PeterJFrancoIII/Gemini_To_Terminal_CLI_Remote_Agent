# Shared Cognitive Memory — Universal Agent Rules

> **Canonical operating authority:**
> https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory
>
> Every Gemini, GPT/ChatGPT, Codex, Antigravity, or other authorized agent performing Shared Memory MCP work MUST consult this GitHub reference before substantial Shared Memory work and MUST cite it when performing Shared Memory architecture or coordination work.

## 1. GitHub-Canonical Guidance
- This GitHub directory is the canonical public operating specification for the Shared Cognitive Memory system.
- Future chats and agents must use it as their guidance rather than relying solely on remembered instructions, copied prompts, stale handoffs, or local prose.
- Required architecture/coordination citation:
  `Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`
- If observed runtime behavior conflicts with these docs, report the discrepancy and resolve it explicitly; never silently redefine the canonical system.

## 2. Single Source of Truth
- Use only the canonical Shared Cognitive Memory graph for cognitive state.
- Never create secondary memory stores, shadow databases, or alternate graph files.
- `InterAgent_Dialogue_Channel` is the sole normal inter-agent communication bus. Never create alternate dialogue channels.

## 3. Retrieval Protocol
- Normal retrieval: `search_nodes` -> `open_nodes`.
- Query the relevant project/session before substantial work.
- Query `InterAgent_Dialogue_Channel` for relevant handoffs or coordination.
- `read_graph` is exceptional and permitted only for justified `debug` or `recovery` with an explicit reason.

## 4. Inter-Agent Communication
Every message to `InterAgent_Dialogue_Channel` must begin:

`[TIMESTAMP | SOURCE -> DESTINATION | MSG:<unique-id> | SESSION:<canonical-session-id>]`

Use a specific agent name or `ALL` as destination. Keep payloads concise. Add `ACTION:` or `ACK:` only when needed.

## 5. Mandatory Provenance Citation
Whenever using another agent's findings, decisions, benchmarks, instructions, or state, cite the exact Shared Memory source:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

For Shared Memory MCP architecture/coordination work, also cite the canonical GitHub rules:

`Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

Never present peer-agent work as unsourced knowledge.

## 6. Writing State
Promote only durable, verified state: architecture decisions, empirical findings, configuration changes, completed milestones, blockers, and handoffs. Never store routine chatter, bulk logs, secrets, or tool dumps.

## 7. Supersession
Never silently contradict canonical state. When state changes, declare:

`SUPERSEDES: <prior entity/message/state>`

Preserve historical provenance.

## 8. Security
Never store passwords, API keys, bearer tokens, private keys, credential-bearing URLs, or unnecessary sensitive data. Store only abstract secret references when required. Never expose credentials in logs, handoffs, GitHub documentation, or citations.

## 9. MCP Integrity and Capability Surface
- All cognitive-memory reads/writes must pass through the hardened MCP.
- Never edit `memory.json` directly.
- Never restore or invoke `delete_*` tools or the retired stock 9-tool memory server.
- Canonical cognitive-memory tools: `create_entities`, `create_relations`, `add_observations`, `search_nodes`, `open_nodes`, `read_graph`.
- Canonical safe source-inspection tools: `read_shared_memory_file(path)`, `list_shared_memory_files()`.
- Source inspection must remain static-allowlist, read-only, and fail closed for private graph data, credentials, traversal, symlink escape, arbitrary files, writes, deletes, shell, and execution.
- Never claim a tool is available merely because the canonical specification defines it; report the actual client-discovered tool surface when diagnosing integrations.
- Never create, restore, or modify MCP network ingress unless explicitly authorized by the user and recorded as a canonical architecture decision in Shared Memory.

## 10. Session Isolation
Operate only within the exact canonical session ID. Never guess IDs or mix unrelated sessions.

## 11. Handoff Validation
Inter-agent dialogue is coordination evidence, not automatically canonical truth. Validate material handoff claims against the relevant canonical entity and/or empirical runtime state before promoting them.

## 12. Agent Lifecycle
Before substantial Shared Memory work:

canonical GitHub rules -> identify exact session -> `search_nodes`/`open_nodes` -> check relevant dialogue -> cite peer provenance -> execute/verify -> write back only materially changed state -> post concise handoff when needed.
