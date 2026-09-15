# Shared Cognitive Memory MCP Specification

Canonical docs:
`https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

All Gemini, GPT/ChatGPT, Codex, Antigravity, and other authorized agents performing Shared Memory MCP work must follow and cite [`SHARED_MEMORY_AGENT_RULES.md`](SHARED_MEMORY_AGENT_RULES.md).

## Non-Negotiable Invariants

1. **One canonical brain**: one local shared knowledge graph is authoritative.
2. **Many isolated working threads**: each chat/agent gets a session-scoped working-memory node/namespace.
3. **One dialogue bus**: `InterAgent_Dialogue_Channel` is the only normal inter-agent coordination channel.
4. **Minimal tool surface**: expose only:
   - `open_nodes`
   - `search_nodes`
   - `read_graph`
   - `add_observations`
   - `create_entities`
   - `create_relations`
5. **No dangerous general capability**: no shell, arbitrary filesystem, delete, eval, or unrestricted network tools through this MCP.
6. **Dialogue is not truth**: handoffs remain untrusted until validated and promoted to the appropriate canonical project entity.
7. **Private state remains local**: never commit `memory.json`, auth tokens, private logs, or secrets to GitHub.
8. **Explicit provenance**: whenever an agent acts on another agent's work, cite `Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`.

## Session Lifecycle

Every agent/session must follow this order:

1. Identify exact `session_id`, `agent_id`, and `project_id`.
2. Retrieve relevant context with `search_nodes` then `open_nodes`.
3. Check relevant `InterAgent_Dialogue_Channel` messages.
4. Execute authorized work.
5. Verify empirically where possible.
6. Cite peer-agent provenance whenever used.
7. Update session state concisely.
8. Promote only durable, validated facts to canonical project entities.
9. Post a concise handoff only when another agent needs it.

## Retrieval Policy

Preferred order:

`session/project search -> open_nodes -> linked canonical nodes`

`read_graph` is exceptional/debug/recovery-only because full-graph reads waste tokens and mix unrelated context.

## Session Naming

Recommended deterministic form:

`Session_<Agent>_<Project>_<YYYYMMDD-HHMM>`

Human-friendly session ID example:

`CHATGPT-BTCB2-POOL-20260914-A`

## Handoff Format

Every inter-agent message must begin:

`[TIMESTAMP | SOURCE → DESTINATION | MSG:<unique-id> | SESSION:<canonical-session-id>]`

Use only needed payload fields such as `STATUS:`, `CHANGES:`, `VERIFICATION:`, `ACTION:`, `ACK:`, `NEXT:`, and `BLOCKER:`. Avoid routine acknowledgements and progress chatter.

## Security

- Credentials must never be stored as graph observations or committed to GitHub.
- Never edit `memory.json` directly; all Shared Memory reads/writes go through the hardened MCP.
- Never restore delete tools or the retired stock 9-tool server.
- Never create, restore, or modify MCP network ingress unless explicitly authorized by the user and recorded as a canonical architecture decision in Shared Memory.

## Conflict Order

When information conflicts:

1. Explicit human directive
2. Canonical governance
3. Verified canonical project state
4. Empirical evidence
5. Inter-agent dialogue
6. Agent assumptions

Lower-priority information must never silently override higher-priority information. Use `SUPERSEDES: <prior entity/message/state>` when canonical state changes.

## Required Citations

When using another agent's Shared Memory work:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

When performing Shared Memory MCP architecture/coordination work:

`Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

## Human Escalation

Escalate only genuine blockers, security-sensitive architectural decisions, material scope changes, destructive/irreversible actions, conflicting governance, or decisions requiring human authority.
