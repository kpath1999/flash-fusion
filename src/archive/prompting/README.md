# Prompting Layer

Purpose: render high-signal prompts based on intent, data summaries, and template catalog.

Implement in promptBuilder.js
- select template from src/config/prompt_templates.yml using intentId and modality (summary vs. insight).
- inject structured fields: stats, top clusters, time ranges, guardrails, and user query.
- return rendered prompt plus metadata (templateId, variables used, truncation info).

Logging
- write rendered prompts to logs/prompt.log as JSONL with templateId, intentId, and checksum of context payload.
