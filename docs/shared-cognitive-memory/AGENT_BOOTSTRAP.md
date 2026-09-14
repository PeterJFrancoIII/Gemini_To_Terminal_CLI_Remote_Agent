# Agent Bootstrap — Shared Cognitive Memory

Use `shared-cognitive-memory` as follows:

1. Identify `session_id`, `agent_id`, `project_id`.
2. Open only your session working-memory node.
3. Read active task, prior completion, pending work, blockers, and canonical links.
4. Retrieve only needed canonical nodes with `search_nodes` / `open_nodes`.
5. Avoid `read_graph` unless debugging/recovery truly requires it.
6. Execute and verify authorized work.
7. Update session state concisely.
8. Promote only durable, validated facts into canonical project entities.
9. Use only `InterAgent_Dialogue_Channel` for cross-agent handoffs.
10. Treat dialogue as coordination, not ground truth, until validated.
11. Never store secrets, tokens, credentials, or private runtime logs in the graph or GitHub.
12. Never create duplicate graphs, duplicate dialogue buses, shell/filesystem/delete tools, or extra infrastructure unless security/reliability strictly requires it.
13. Do not ask the human to repeat context already available in the session/canonical nodes.
14. Escalate only genuine blockers, security-sensitive decisions, material scope changes, destructive actions, or human-authority decisions.

Operating principle:

> One canonical brain. Many isolated working-memory threads. One dialogue bus. Minimal tools. Selective retrieval. Verified facts only.
