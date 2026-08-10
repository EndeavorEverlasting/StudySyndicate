# Skill: Public Claim Intake

## Trigger

Use when ParallaxPort or another public career surface adds, removes, renames, or materially changes
a technical claim.

## Required inputs

- public source name
- claim text/category as actually presented
- snapshot date
- existing StudySyndicate track or reason a new bounded track is required

## Procedure

1. Capture only public professional claims; do not copy credentials, private analytics, visitor data,
   environment values, or other secrets.
2. Update the versioned source adapter under `harness/sources/`.
3. Reuse existing StudySyndicate authorities before creating a new curriculum.
4. Give each claim one smallest `firstPractice` action.
5. Set a state from evidence; new claims default to `exposed`.
6. Run `python scripts/harness.py study-fodder`.
7. Run `python scripts/harness.py validate --level quick`.
8. Review the generated report for accidental overclaiming.

## Expected outputs

- updated source adapter
- regenerated operator report
- passing source/target validation
- clear next practice action for every claim

## Boundary

This skill updates StudySyndicate's interpretation of a public claim. It does not mutate the source
portfolio repository or website.
