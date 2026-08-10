# Skill: Documentation Lookup Without Solution Leakage

## Trigger

Use when the learner understands the task conceptually but is blocked on syntax, an API signature,
a language rule, or an error message.

## Required inputs

- language/tool/library
- exact syntax or behavior question
- current attempt or smallest failing snippet
- current study mode

## Procedure

1. Write the narrow question before searching.
2. Prefer the official language, standard-library, framework, or database documentation.
3. Search for the API/construct, not the challenge name.
4. Read only enough to answer:
   - signature or syntax
   - parameter/input meaning
   - return/output behavior
   - one minimal example when needed
5. Close or move away from the docs.
6. Reconstruct the needed line or concept in the learner's own attempt.
7. Run the smallest relevant test.
8. Record the source name, topic looked up, and what changed.

## Search-query templates

- `official Python docs dictionary membership`
- `official Python docs enumerate`
- `official PostgreSQL documentation GROUP BY HAVING`
- `official React docs state update`
- `<tool> official docs <exact API or error phrase>`

Do not search `<challenge name> solution` during a docs-assisted or mastery session.

## Output

A short evidence note containing:

- question
- source/topic consulted
- answer in the learner's own words
- resulting code/query change
- test result

## Mastery boundary

A docs-assisted attempt can prove learning progress but not a no-reference reconstruction gate.
Schedule a later blank-file attempt before marking the skill `defensible`.
