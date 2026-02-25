# Config Catalogs

- intent_catalog.json: constrained intent set, keywords, and weights; used by intentParser.
- prompt_templates.yml: prompt blocks keyed by templateId and intent; include variables and guardrails.
- fallback_policies.yml: ordered policies for OOS handling; define thresholds and behaviors.

Edit these files to iterate on experiments without touching application code.
