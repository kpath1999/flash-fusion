# Intent Layer

Purpose: map user queries into the constrained intent set and emit structured context for prompting.

Implement in intentParser.js
- normalize query, score against catalog (src/config/intent_catalog.json), choose top intent.
- emit: { intentId, scores, confidence, rationale, isOutOfScope (bool) }.
- log decisions via src/utils/logger.writeJsonl('intent.log', ...).

Notes
- Keep the catalog small and well-described; prefer deterministic keyword/regex + lightweight ML if needed.
- Include thresholds for OOS detection; pass through to fallback layer.
