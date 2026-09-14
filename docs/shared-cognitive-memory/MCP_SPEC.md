# Shared Cognitive Memory MCP Specification

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
6. **Dialogue is not truth**: handoffs and coordination remain untrusted until validated and promoted to the appropriate canonical project entity.
7. **Private state remains local**: never commit `memory.json`, auth tokens, private logs, or secrets to GitHub.

## Session Lifecycle

Every agent/session must follow this order:

1. Identify `session_id`, `agent_id`, and `project_id`.
2. Open the session working-memory node.
3. Read active task, last completed work, pending work, blockers, and canonical links.
4. Retrieve only required canonical nodes with `search_nodes` / `open_nodes`.
5. Execute authorized work.
6. Verify empirically where possible.
7. Update the session state concisely.
8. Promote only durable, validated facts to canonical project entities.
9. Post a concise handoff to `InterAgent_Dialogue_Channel` only when another agent needs it.

## Retrieval Policy

Preferred order:

`session node -> linked canonical nodes -> search_nodes -> open_nodes`

`read_graph` is exceptional/debug/recovery-only because full-graph reads waste tokens and mix unrelated context.

## Session Naming

Recommended deterministic form:

`Session_<Agent>_<Project>_<YYYYMMDD-HHMM>`

Human-friendly session ID example:

`CHATGPT-BTCB2-POOL-20260914-A`

## Handoff Format

Use only needed fields:

```text
[TIMESTAMP | Agent -> Agent]
STATUS: <current state>
CHANGES: <exact changes>
VERIFICATION: <tests/evidence>
NEXT: <next action>
BLOCKER: <only if applicable>
```

Avoid routine acknowledgements and progress chatter.

## Security

- MCP transport must be authenticated and encrypted when it leaves the local device.
- The local service should bind to loopback unless LAN exposure is explicitly required.
- Unauthorized requests must be rejected.
- Credentials must never be stored as graph observations.
- A remote transport is a path to the local MCP, not a data store and not canonical memory.

## Conflict Order

When information conflicts:

1. Explicit human directive
2. Canonical governance
3. Verified canonical project state
4. Empirical evidence
5. Inter-agent dialogue
6. Agent assumptions

Lower-priority information must never silently override higher-priority information.

## Human Escalation

Escalate only for genuine blockers, security-sensitive architectural decisions, material scope changes, destructive/irreversible actions, conflicting governance, or decisions requiring human authority.
