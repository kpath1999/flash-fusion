# Experiment: Out-of-Scope + Fallbacks

Goals
- Detect queries that exceed available data or cluster coverage.
- Compare fallback behaviors: reject with explanation vs. raw-data fetch vs. cheap classifier/RAG.

Suggested steps
1) Curate OOS queries and expected behaviors.
2) Implement `detectOutOfScope` and fallback policies in `src/fallbacks/`.
3) Log decisions to intent.log and prompt.log for analysis.
4) Document outcomes and user-facing copy for the paper.
