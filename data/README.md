# Data Layout

- raw/: source telemetry (CSV, JSONL) straight from collection; keep originals read-only.
- processed/: derived artifacts (GeoJSON, cluster outputs, metrics) that can be regenerated from raw.
- snapshots/: frozen copies of intermediate models or experiment outputs used for the paper.

Notes
- Update scripts to read from raw/ and write to processed/.
- When promoting a processed artifact to a snapshot for the paper, copy it into snapshots/ with a dated filename and brief note.
