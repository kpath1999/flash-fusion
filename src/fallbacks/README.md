# Fallbacks / Out-of-Scope

Purpose: decide what to do when a query cannot be satisfied by current data/cluster scope.

Implement in fallbackRouter.js
- detectOutOfScope(query, intentResult, dataAvailability) -> { isOOS, reason, policyId }.
- apply policy from src/config/fallback_policies.yml: reject, raw-data fetch, cheap classifier, or RAG.
- return user-facing message plus any follow-up actions (e.g., run convert_to_geojson, fetch raw slice).

Logging
- log OOS decisions to intent.log; log any fallback prompts to prompt.log with policyId.
