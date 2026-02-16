# Logs

- prompt.log: JSONL of prompts sent to the LLM (include intent, template, timestamp, hash of context).
- intent.log: JSONL of query->intent classification decisions (scores, chosen intent, oos flag).

Guidelines
- Use structured JSON per line for downstream analysis.
- Avoid storing raw PII; hash user ids if needed.
