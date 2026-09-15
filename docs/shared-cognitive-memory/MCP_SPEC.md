# Shared Cognitive Memory MCP Specification

**Canonical operating specification:**
https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory

Every Gemini, GPT/ChatGPT, Codex, Antigravity, and other authorized agent performing Shared Memory MCP work must consult and follow `SHARED_MEMORY_AGENT_RULES.md`. Shared Memory architecture/coordination work must cite this canonical GitHub directory.

## Non-Negotiable Invariants

1. **One canonical brain:** one local shared knowledge graph is authoritative for cognitive state.
2. **Many isolated working threads:** each chat/agent gets an exact session-scoped working context.
3. **One dialogue bus:** `InterAgent_Dialogue_Channel` is the only normal inter-agent coordination channel.
4. **Selective retrieval:** normal reads use `search_nodes` -> `open_nodes`; `read_graph` is justified debug/recovery-only.
5. **Minimal capability:** expose only narrowly scoped cognitive-memory and approved read-only inspection capabilities.
6. **No dangerous general capability:** no shell, arbitrary filesystem, delete, eval, unrestricted execution, or unrestricted network capability through this MCP.
7. **Dialogue is not truth:** handoffs remain coordination evidence until validated and promoted to appropriate canonical state.
8. **Private state remains private:** never commit `memory.json`, backups, credentials, auth tokens, private logs, or credential-bearing URLs to GitHub.
9. **Explicit provenance:** whenever an agent acts on another agent's work, cite `Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`.
10. **GitHub-canonical guidance:** this directory is the public operating authority future agents must consult and cite.

## Canonical Capability Model

### Cognitive-memory graph tools

1. `open_nodes`
2. `search_nodes`
3. `read_graph`
4. `add_observations`
5. `create_entities`
6. `create_relations`

There are no delete graph tools. `read_graph` is exceptional and requires explicit debug/recovery justification.

### Safe source-inspection tools

7. `read_shared_memory_file(path)`
8. `list_shared_memory_files()`

These are not arbitrary filesystem tools. They must be read-only and backed by a static allowlist. Implementations must reject private graph data, backups, credentials, auth tokens, logs, temporary/lock files, absolute paths, traversal, NUL/backslash bypasses, symlink escape, writes, deletes, shell, and execution. Boundary validation must fail closed.

A client may temporarily discover fewer capabilities because of stale registration, transport differences, permission policy, or intentional client limitation. Agents must distinguish the canonical contract from the empirically discovered client surface and report discrepancies.

## Session Lifecycle

Every agent/session must follow this order:

1. Consult the canonical GitHub documentation.
2. Identify exact `session_id`, `agent_id`, and `project_id`.
3. Retrieve relevant context with `search_nodes` then `open_nodes`.
4. Check relevant `InterAgent_Dialogue_Channel` messages.
5. Execute authorized work.
6. Verify empirically where possible.
7. Cite peer-agent provenance whenever used.
8. Update session state concisely.
9. Promote only durable, validated facts to canonical project entities.
10. Post a concise handoff only when another agent needs it.

## Retrieval Policy

Preferred order:

`session/project search -> open_nodes -> linked canonical nodes`

`read_graph` is exceptional/debug/recovery-only because full-graph reads waste tokens and mix unrelated context.

## Handoff Format

Every inter-agent message must begin:

`[TIMESTAMP | SOURCE -> DESTINATION | MSG:<unique-id> | SESSION:<canonical-session-id>]`

Use only needed payload fields such as `STATUS:`, `CHANGES:`, `VERIFICATION:`, `ACTION:`, `ACK:`, `NEXT:`, and `BLOCKER:`. Avoid routine acknowledgements and progress chatter.

## Transport and Network Ingress

Transport is separate from the cognitive-memory contract.

- Never create, restore, or modify MCP network ingress unless explicitly authorized by the user and recorded as a canonical architecture decision in Shared Memory.
- A transport exception does not authorize broader tools or weaker graph security.
- Never commit or reproduce live connector credentials or credential-bearing URLs.
- Retired credentials must not be reused merely because a client cache still accepts them.
- When transport behavior differs among ChatGPT, Gemini/Antigravity, Codex, or other clients, record and diagnose the observed surface independently rather than conflating them.

## Security

- Credentials must never be stored as graph observations or committed to GitHub.
- Never edit `memory.json` directly; cognitive-memory reads/writes go through the hardened MCP.
- Never restore delete tools or the retired stock 9-tool server.
- Source inspection is allowlisted read-only access, not permission to inspect the private graph or arbitrary host files.
- Unknown/malformed requests and unknown record formats must fail closed.
- Durable writes must preserve integrity under concurrency and atomic replacement.

## Conflict Order

When information conflicts:

1. Explicit human directive
2. Canonical GitHub governance/specification
3. Verified canonical Shared Memory project/session state
4. Empirical runtime evidence
5. Inter-agent dialogue
6. Agent assumptions or remembered context

Lower-priority information must never silently override higher-priority information. Use `SUPERSEDES: <prior entity/message/state>` when canonical state changes. If runtime evidence shows the GitHub specification is stale, report the discrepancy and update governance through an authorized change rather than silently diverging.

## Required Citations

When using another agent's Shared Memory work:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

When performing Shared Memory MCP architecture/coordination work:

`Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

## Human Escalation

Escalate only genuine blockers, security-sensitive architectural decisions, material scope changes, destructive/irreversible actions, conflicting governance, or decisions requiring human authority.
