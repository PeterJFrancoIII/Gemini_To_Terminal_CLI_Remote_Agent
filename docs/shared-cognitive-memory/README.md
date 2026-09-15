# Shared Cognitive Memory MCP

Canonical operating documentation for the local `shared-cognitive-memory` MCP used by Gemini/Antigravity, GPT/ChatGPT, Codex, and other authorized agents.

## Quick Reference for Agents

**Canonical documentation:**
`https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

Before performing Shared Memory MCP work, every agent MUST:

1. Read [`SHARED_MEMORY_AGENT_RULES.md`](SHARED_MEMORY_AGENT_RULES.md).
2. Identify the exact canonical session/project ID.
3. Retrieve context with `search_nodes` → `open_nodes`.
4. Check `InterAgent_Dialogue_Channel` when peer-agent work may exist.
5. Cite peer-agent provenance whenever using it:
   `Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`
6. Cite these canonical operating rules when performing MCP architecture/coordination work:
   `Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`
7. Write back only materially changed, verified state.

## Architecture

- **One canonical local graph**: `memory.json` remains the sole authoritative data store on the local host.
- **Many isolated session working sets**: sessions retrieve only relevant project/session state.
- **One inter-agent bus**: `InterAgent_Dialogue_Channel`.
- **Six MCP tools only**:
  - `create_entities`
  - `create_relations`
  - `add_observations`
  - `search_nodes`
  - `open_nodes`
  - `read_graph`
- No delete, shell, arbitrary filesystem, eval, or general execution capability through this MCP.

## Retrieval & Writing

Normal retrieval:

`search_nodes` → `open_nodes`

`read_graph` is exceptional and reserved for justified `debug` or `recovery` use.

Promote only durable verified state: decisions, empirical findings, configuration changes, milestones, blockers, and concise handoffs. Preserve history and explicitly mark superseded state.

## Inter-Agent Communication

All normal cross-agent coordination uses `InterAgent_Dialogue_Channel` with:

`[TIMESTAMP | SOURCE → DESTINATION | MSG:<unique-id> | SESSION:<canonical-session-id>]`

When another agent's work is used, cite the exact source:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

## Security

Private runtime data must never be committed to GitHub, including:

- `memory.json` and backups
- auth/API/runtime tokens
- private keys
- credential-bearing URLs
- private logs
- machine-specific secrets

Never edit `memory.json` directly; use the hardened MCP. Never restore delete tools or the retired stock 9-tool memory server. Never alter MCP network ingress unless explicitly authorized by the user and recorded as a canonical architecture decision.

## Subsystems / Reference Files

- [`SHARED_MEMORY_AGENT_RULES.md`](SHARED_MEMORY_AGENT_RULES.md) — universal rules every agent must follow and cite.
- [`AGENT_BOOTSTRAP.md`](AGENT_BOOTSTRAP.md) — minimal startup checklist.
- [`MCP_SPEC.md`](MCP_SPEC.md) — architecture, invariants, retrieval, session, handoff, and security specification.

## Fast Bootstrap

For a new agent or session:

1. Load this README and `SHARED_MEMORY_AGENT_RULES.md`.
2. Resolve the canonical session ID; never guess it.
3. `search_nodes` for the session/project.
4. `open_nodes` only the relevant matches.
5. Check relevant `InterAgent_Dialogue_Channel` messages.
6. Perform and verify work.
7. Cite any peer-agent source used.
8. Write only material state changes back through MCP.

Operating principle:

> One canonical brain. Many isolated working threads. One dialogue bus. Minimal tools. Selective retrieval. Explicit provenance.
