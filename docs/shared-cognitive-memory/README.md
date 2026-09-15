# Shared Cognitive Memory MCP

> **CANONICAL SYSTEM OF RECORD FOR OPERATING GUIDANCE**
>
> This directory is the authoritative public specification for how Gemini/Antigravity, GPT/ChatGPT, Codex, and every other authorized agent must use the Shared Cognitive Memory MCP.
>
> Canonical URL: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory

## Mandatory Rule for Every Future Agent / Chat

Before performing Shared Memory work, an agent MUST consult this GitHub directory and follow `SHARED_MEMORY_AGENT_RULES.md`. Any Shared Memory architecture, coordination, handoff, or implementation work MUST cite:

`Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

When another agent's Shared Memory work is used, also cite its exact provenance:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

If remembered instructions, old handoffs, local notes, or prior chat text conflict with this canonical GitHub specification, agents must stop and resolve the conflict using the precedence rules in `MCP_SPEC.md`; they must not silently substitute stale behavior.

## Canonical Architecture

- **One canonical brain:** one local `memory.json` graph is the authoritative private data store.
- **Many isolated working threads:** each chat/agent operates only in its exact canonical session/project context.
- **One coordination bus:** `InterAgent_Dialogue_Channel`.
- **Hardened MCP only:** agents never edit `memory.json` directly.
- **Selective retrieval:** `search_nodes` -> `open_nodes` is the normal retrieval path.
- **Exceptional graph dump:** `read_graph` is debug/recovery-only and requires justification.
- **Private data stays private:** graph data, credentials, private logs, tokens, and credential-bearing URLs are never published to GitHub.

### Canonical Tool Classes

The hardened local runtime has two capability classes:

**Six cognitive-memory graph tools**
1. `create_entities`
2. `create_relations`
3. `add_observations`
4. `search_nodes`
5. `open_nodes`
6. `read_graph`

**Two safe read-only source-inspection tools**
7. `read_shared_memory_file(path)`
8. `list_shared_memory_files()`

The inspection tools are strictly allowlisted and must fail closed for `memory.json`, backups, credentials, tokens, logs, temporary/lock files, path traversal, absolute paths, symlink escape, arbitrary filesystem access, writes, deletes, shell, or execution.

A client exposing fewer than these eight tools may be stale, incompletely registered, or intentionally capability-limited. An agent must report the observed tool surface rather than pretending unavailable tools exist.

## Network / Transport Governance

Network ingress is not implicitly authorized. Never create, restore, or modify Shared Memory MCP network ingress unless the user explicitly authorizes it and the change is recorded as a canonical architecture decision in Shared Memory.

Transport configuration is separate from the cognitive-memory contract. A transport workaround must never weaken graph isolation, tool restrictions, credential handling, or provenance requirements. Never publish live credentials or credential-bearing connector URLs.

## Agent Bootstrap

Every new agent/session must:

1. Read this README and `SHARED_MEMORY_AGENT_RULES.md` from the canonical GitHub location.
2. Resolve the exact canonical session ID; never guess it.
3. Retrieve relevant state using `search_nodes` -> `open_nodes`.
4. Check relevant `InterAgent_Dialogue_Channel` handoffs when peer work may exist.
5. Validate handoff claims before promoting them to canonical state.
6. Perform and verify the authorized work.
7. Cite peer-agent provenance used.
8. Cite this GitHub rules directory for Shared Memory architecture/coordination work.
9. Write back only materially changed, verified state.
10. Explicitly supersede obsolete state rather than silently overwriting history.

## Canonical Documents

- `SHARED_MEMORY_AGENT_RULES.md` — mandatory universal operating rules.
- `MCP_SPEC.md` — architecture, invariants, capability model, conflict precedence, security, and lifecycle specification.
- `AGENT_BOOTSTRAP.md` — concise startup procedure.

Operating principle:

> **One canonical brain. Many isolated working threads. One dialogue bus. Minimal capabilities. Selective retrieval. Explicit provenance. GitHub-canonical operating guidance.**
