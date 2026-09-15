# Shared Cognitive Memory MCP — Agent Reference

This repository contains the canonical public operating documentation for the local Shared Cognitive Memory MCP used by Gemini/Antigravity, GPT/ChatGPT, Codex, and other authorized agents.

**Canonical Shared Memory docs:** [`docs/shared-cognitive-memory/`](docs/shared-cognitive-memory/)

Agents performing Shared Memory MCP work MUST begin with:

1. [`docs/shared-cognitive-memory/README.md`](docs/shared-cognitive-memory/README.md) — quick reference and subsystem map.
2. [`docs/shared-cognitive-memory/SHARED_MEMORY_AGENT_RULES.md`](docs/shared-cognitive-memory/SHARED_MEMORY_AGENT_RULES.md) — mandatory universal rules.
3. [`docs/shared-cognitive-memory/AGENT_BOOTSTRAP.md`](docs/shared-cognitive-memory/AGENT_BOOTSTRAP.md) — minimal startup sequence.
4. [`docs/shared-cognitive-memory/MCP_SPEC.md`](docs/shared-cognitive-memory/MCP_SPEC.md) — architecture and invariants.

Required provenance when using another agent's Shared Memory work:

`Shared Memory: <SESSION/ENTITY> | MSG:<message-id>`

Required canonical-rules citation for Shared Memory MCP architecture/coordination work:

`Shared Memory MCP Rules: https://github.com/PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent/tree/main/docs/shared-cognitive-memory`

Private runtime state such as `memory.json`, credentials, keys, private logs, and machine-specific secrets must never be committed to GitHub.

---

# Terminal-to-Gemini Bridge

Control your system terminal using natural language. Run commands, manage files, and automate tasks just by asking in English.

## Setup

1.  **Get an API Key**:
    *   Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a key.

2.  **Run the App**:
    *   **Windows**: Double-click `Launch_Windows.bat`
    *   **macOS**: Double-click `Launch_macOS.command`
    *   **Linux**: Run `./Launch_Linux.sh`

3.  **Enter Key**:
    *   Paste your API Key when prompted and click "Apply".

## How to Use

*   **Type a Request**: "Find all large files not opened in the last month"
*   **Review**: The app will show you the commands it wants to run.
*   **Execute**: Commands run in your terminal. Risks are color-coded (Red = Dangerous, Green = Safe).

_For technical details and architecture, see [README_DEVELOPER.md](README_DEVELOPER.md)._
