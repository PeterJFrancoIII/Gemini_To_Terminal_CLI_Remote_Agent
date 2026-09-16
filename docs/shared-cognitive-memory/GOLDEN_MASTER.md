# Shared Cognitive Memory — Golden Master

**Locked:** 2026-09-15 (America/New_York)
**Status:** GOLDEN MASTER
**Repository:** `PeterJFrancoIII/Gemini_To_Terminal_CLI_Remote_Agent`
**Canonical path:** `docs/shared-cognitive-memory/`

This directory state is the approved golden master baseline for the Shared Cognitive Memory program. Agents must treat this snapshot as the known-good reference implementation/specification and must not silently redefine its architecture, policy, synchronization model, or agent rules.

## Locked baseline

| File | Git blob SHA |
|---|---|
| `AGENT_BOOTSTRAP.md` | `6a7ea93bf268ad6175dab830abf11ebbd736665b` |
| `MCP_SPEC.md` | `279f5902ab23d32ed944d025432f6f393b8f0c74` |
| `README.md` | `614440461bc8a6eba47bbd3d1746582409728629` |
| `SHARED_MEMORY_AGENT_RULES.md` | `18d91498b44ea6c20b63aa0755aa1bf0096072e0` |

## Verification state

The exposed Shared Cognitive Memory connector completed an end-to-end round-trip test: tool discovery, bounded search, exact-node retrieval, entity creation, observation update, relation creation, search-after-write, and open-after-write all succeeded. Guardrails for unrestricted graph reads and credential-like content also activated as expected.

## Change control

Future work may improve this system, but changes must be explicit and reviewable. Preserve this baseline as the rollback/reference point. Any replacement golden master must document what changed, why it changed, and verification results before superseding this file.

## Multi-agent requirement

ChatGPT, Gemini, and other participating agents must use the canonical Shared Cognitive Memory graph for cross-agent state and follow the rules in this directory. Gemini is specifically instructed through shared memory to recognize this GitHub baseline as the current golden master and mirror the same designation in its working context.
