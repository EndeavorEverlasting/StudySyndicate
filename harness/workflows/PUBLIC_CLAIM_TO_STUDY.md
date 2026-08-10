# Public Claim to Study Workflow

Use this when a technology, framework, database, or capability appears on ParallaxPort or another
public professional surface.

## Purpose

Turn presentation pressure into a bounded practice queue. The workflow does **not** downgrade or
remove public claims automatically and does not treat portfolio text as proof of mastery.

## Procedure

1. Refresh or inspect the versioned source snapshot:
   `harness/sources/parallaxport-claims.v1.json`.
2. Run:
   `python scripts/harness.py study-fodder`.
3. Open:
   `harness/reports/PARALLAXPORT_STUDY_FODDER.md`.
4. Pick one claim based on career relevance and current weakness.
5. Reuse an existing authority:
   - arrays/algorithm reasoning -> `docs/software/ARRAYS_MASTERY.md`
   - SQL/database foundations -> `docs/software/SQL_RUST_FOUNDATIONS.md`
   - existing public technology maintenance -> maintenance lane in the same foundations doctrine
6. Choose `guided`, `docs-assisted`, or `mastery`.
7. Produce one evidence-bearing rep: code/query, runnable check where practical, explanation, and
   a recorded next retrieval target.
8. Change the claim state only from evidence, never from how polished the portfolio looks.

## Source refresh

Use `harness/skills/public-claim-intake/SKILL.md`.

A refresh must be explicit and reviewable. If ParallaxPort and the source snapshot disagree, update
the snapshot in its own bounded change, regenerate the report, and run the harness validator.

## Collision boundary

StudySyndicate owns the study interpretation and evidence contract. ParallaxPort owns its public
presentation. This workflow does not mutate ParallaxPort.
