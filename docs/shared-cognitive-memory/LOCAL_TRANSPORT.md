# Shared Cognitive Memory — Local Transport Architecture

> **Directive Reference:** Authorized Local MCP Migration Directive (October 8, 2026)  
> **Preserved Golden Master:** Commit `7208a34a07bdb2d8de00b327cbb012feb0d3b74c`  
> **Operational Status:** Active / Verified

---

## 1. Preserved Golden Master Baseline

This architectural update operates under explicit user and architect authorization to eliminate third-party public tunneling (ngrok) while strictly preserving the Golden Master baseline:

* **Single Source of Truth:** One canonical local graph file (`memory.json`) remains on the host Mac.
* **8-Tool Contract:** Exposes exactly 6 graph operations (`open_nodes`, `search_nodes`, `read_graph`, `add_observations`, `create_entities`, `create_relations`) plus 2 restricted source inspection tools (`read_shared_memory_file`, `list_shared_memory_files`).
* **Tool Annotations:** Standard MCP read/write risk annotations are maintained (5 Read tools, 3 Write tools).
* **Strict Security Invariants:** Zero delete operations, zero arbitrary shell/filesystem execution, fail-closed access control on sensitive paths, and zero plaintext credentials in repository or graph.

---

## 2. Local Transport Configuration

The remote ngrok public tunnel dependency has been permanently retired. The architecture now standardizes on local, zero-cost, unmetered transports:

```text
                     macOS Host
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     ChatGPT           Gemini           Codex
     Desktop        Antigravity       CLI / App
        │                │                │
        └────────────────┼────────────────┘
                         │
                     LOCAL MCP
                   (Direct STDIO)
                         │
                Hardened MCP Runtime
                (scripts/sse_bridge.js)
                         │
               Canonical Memory Graph
                    (memory.json)
```

### Component Details

1. **Direct STDIO (Primary):**
   * Invocation: `node scripts/sse_bridge.js --stdio`
   * Used natively by Codex CLI (`~/.codex/config.toml`), Gemini/Antigravity MCP runtime, and ChatGPT Desktop local plugins.
   * Zero network latency, zero port exposure, immune to external bandwidth quotas.

2. **Loopback HTTP Bridge (Supervised Local Fallback):**
   * Endpoint: `http://127.0.0.1:8080` (Loopback only; no public interface binding).
   * Managed by macOS launchd: `com.sharedmemory.supervisor` via `scripts/supervisor_daemon.sh`.
   * Enforces strict `Authorization: Bearer <TOKEN>` authentication using credentials from `~/.shared_memory_tunnel_token` (mode `0600`).
   * ngrok startup has been removed from the supervisor script.

3. **ChatGPT Desktop Local Plugin:**
   * Package: `shared-cognitive-memory@local-marketplace`
   * Manifest: `.codex-plugin/plugin.json` declaring `mcpServers: ./.mcp.json` pointing to local stdio runtime.
   * Registered in `~/.codex/config.toml` under `[plugins."shared-cognitive-memory@local-marketplace"]`.

---

## 3. Verified Operational State

| Test Suite / Target | Transport | Result | Verification Notes |
|---|---|---|---|
| Full Regression Suite | Local STDIO / HTTP | **PASS** | 22/22 tests passing (`tests/mcp_runtime.test.js`) |
| Codex CLI (`codex exec`) | Local STDIO | **PASS** | `search_nodes` and `open_nodes` executed live with full response |
| Gemini / Antigravity | Local MCP Tool | **PASS** | `search_nodes`, `open_nodes`, and `add_observations` executed live |
| Safe File Inspection | Local MCP | **PASS** | `list_shared_memory_files` (14 files, including `LOCAL_TRANSPORT.md`); `read_shared_memory_file` (valid allowlist); `memory.json` access denied fail-closed |
| Ingress Retirement | Process / Network | **PASS** | ngrok process terminated; supervisor daemon updated; zero public listener |
| Credential Hygiene | Host Storage | **PASS** | Tunnel token rotated in `~/.shared_memory_tunnel_token`; query string tokens deprecated |

---

## 4. Client-Specific Limitations

* **Desktop Scope:** Local STDIO and loopback HTTP bindings are accessible exclusively to processes running on the local macOS host (`ChatGPT.app`, `codex`, `antigravity`).
* **Remote / Mobile ChatGPT:** ChatGPT Web or mobile apps cannot reach local loopback without OpenAI Secure MCP Tunnel. When remote access is required, OpenAI Secure MCP Tunnel (`tunnel-client`) must be used as the outbound-only transport instead of public ingress tunnels.
