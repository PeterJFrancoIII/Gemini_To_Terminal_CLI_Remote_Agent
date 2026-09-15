# Agent Bootstrap — Shared Cognitive Memory

Canonical docs:
`https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

Before Shared Memory MCP work, read and follow [`SHARED_MEMORY_AGENT_RULES.md`](SHARED_MEMORY_AGENT_RULES.md) and cite the canonical docs when performing MCP architecture/coordination work.

Use `shared-cognitive-memory` as follows:

1. Identify the exact `session_id`, `agent_id`, and `project_id`; never guess or mix sessions.
2. Retrieve context with `search_nodes` → `open_nodes`.
3. Check `InterAgent_Dialogue_Channel` when peer-agent work may exist.
4. Avoid `read_graph` unless justified `debug`/`recovery` requires it.
5. Execute and empirically verify authorized work.
6. Cite peer-agent provenance whenever used:
   `Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`
7. Update session/canonical state only when materially changed and verified.
8. Promote only durable facts, decisions, configuration, milestones, blockers, and handoffs.
9. Use only `InterAgent_Dialogue_Channel` for cross-agent coordination.
10. Never store secrets, tokens, credentials, private keys, credential-bearing URLs, or private bulk logs.
11. Never edit `memory.json` directly, create duplicate graphs/dialogue buses, restore delete tools, or bypass the hardened MCP.
12. Never create, restore, or modify MCP network ingress unless explicitly authorized by the user and recorded as a canonical architecture decision.
13. Do not ask the human to repeat context already available in the relevant session/canonical nodes.
14. Escalate only genuine blockers, security-sensitive decisions, material scope changes, destructive actions, or human-authority decisions.

Operating principle:

> One canonical brain. Many isolated working-memory threads. One dialogue bus. Minimal tools. Selective retrieval. Explicit provenance.
