# Shared Cognitive Memory MCP

Canonical operating documentation for the local `shared-cognitive-memory` MCP used by ChatGPT, Antigravity/Gemini, and other authorized agents.

## Architecture

- **One canonical local graph**: persistent shared knowledge remains on the local device.
- **Many isolated session working sets**: each chat/agent session reads only its own working memory plus explicitly relevant canonical nodes.
- **One inter-agent bus**: `InterAgent_Dialogue_Channel`.
- **Six MCP tools only**: `open_nodes`, `search_nodes`, `read_graph`, `add_observations`, `create_entities`, `create_relations`.
- No shell, arbitrary filesystem, delete, eval, or general execution capability through this MCP.

## Data vs Transport

The canonical memory store is local. Remote agents may require an authenticated encrypted transport to reach the local MCP endpoint. Transport must never become a second source of truth.

Private runtime data such as `memory.json`, auth tokens, logs containing private context, and machine-specific secrets must **not** be committed to GitHub.

## Agent Rule

Before substantial work: determine your session ID, load only its working set, then selectively retrieve relevant canonical nodes with `search_nodes` / `open_nodes`.

Avoid `read_graph` during normal work. It exists for exceptional diagnostic/recovery use only.

See [`MCP_SPEC.md`](MCP_SPEC.md) and [`AGENT_BOOTSTRAP.md`](AGENT_BOOTSTRAP.md).
