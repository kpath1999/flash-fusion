# Experiment: Query -> Intent -> Prompt

Goals
- Measure accuracy of intent mapping against a labeled set of queries.
- Evaluate prompt template selection and rendered prompt quality.

Suggested steps
1) Add labeled queries and expected intents (CSV/JSON) here.
2) Wire `src/intent/intentParser.js` to load configs and emit scores.
3) Render prompts with `src/prompting/promptBuilder.js`; save samples to prompt.log.
4) Summarize findings (precision/recall, prompt clarity) for the paper.
