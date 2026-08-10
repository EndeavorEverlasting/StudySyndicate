# ParallaxPort Study Fodder

Source snapshot: **ParallaxPort** on **2026-08-10**.

> Public presentation is a study-priority signal, not proof of mastery.

Use `python scripts/harness.py start guided-study` when a target feels too difficult to begin.

## Programming Languages

### Python
- State: `exposed`
- Study targets: `arrays-mastery`, `software-foundations-maintenance`
- First practice: Use guided Two Sum in Python, then explain dictionary membership and complexity.

### JavaScript
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Write a frequency-map array drill and explain object/Map lookup tradeoffs.

### TypeScript
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Type a small array transform with explicit input/output types and one failing test.

### Java
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Rebuild a small array scan and explain value/reference behavior relevant to the solution.

### C
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Implement a bounded array scan and explain indices, memory bounds, and failure cases.

## Data Science & Analytics

### Pandas
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Load a tiny table, filter rows, group once, and explain the resulting shape from memory.

### NumPy
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Create one vectorized array operation and explain shape, dtype, and broadcasting.

### Matplotlib
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Build one plot from a small dataset and explain figure/axes responsibilities.

## Web Development

### React
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Build or explain a tiny state-to-view loop and identify one stale-state failure mode.

### Django
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Trace one request through URL routing, view, model/query, and response.

### Flask
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Explain the ParallaxPort request path from Flask route to Jinja response without reading the answer first.

### Node.js
- State: `exposed`
- Study targets: `software-foundations-maintenance`
- First practice: Explain the event loop at a practical level and write one small async I/O example.

## Databases

### PostgreSQL
- State: `exposed`
- Study targets: `sql`
- First practice: Write filtering, join, aggregation, and transaction drills using PostgreSQL-compatible SQL.

### MySQL
- State: `exposed`
- Study targets: `sql`
- First practice: Practice the shared SQL foundations, then note one MySQL-specific behavior only when encountered.

### SQLite
- State: `exposed`
- Study targets: `sql`, `taskq`
- First practice: Use SQLite for the taskq schema/CRUD path and explain transaction boundaries.

## How to use this report

1. Pick one claim.
2. Choose `guided`, `docs-assisted`, or `mastery`.
3. Perform one bounded rep.
4. Run the relevant validator/test.
5. Record what you could do from memory, what help you used, and the next retrieval target.

Regenerate after an intentional source snapshot update:

```bash
python scripts/harness.py study-fodder
```
