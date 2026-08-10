# Guided Study Workflow

Use this when the learner does not know how to begin, cannot reconstruct the assignment from memory,
or needs feedback without immediately seeing a solution.

## Non-negotiable packet order

A guided exercise must not begin with vague questions such as "What comes in?" before presenting the
assignment. Every problem packet establishes context in this order:

1. **Premise** — what problem the learner is solving.
2. **Inputs** — what data is provided.
3. **Output** — what must be returned or produced.
4. **Guarantees and constraints** — rules that change what counts as correct.
5. **Worked example of the contract** — demonstrate input/output meaning without implementation code.
6. **Learning goal and allowed help** — explain what this rep is practicing.
7. **Guided checkpoints** — only now ask the learner to reason or code.
8. **Executable feedback, hints, and documentation path** — make the next move obvious when stuck.

The UI is deferred until these mechanics have repeated operator proof. A future UI must render this
contract; it must not invent, omit, or hide the premise and feedback mechanics.

## The three modes

### Guided

Use this first when the task feels daunting. Premise, examples, decomposition, graduated hints,
official documentation, and executable feedback are allowed. The goal is a first successful loop.

### Docs-assisted

Attempt first, then consult official documentation for syntax/API facts. Record what was looked up.
Do not search for the exact challenge solution.

### Mastery

Use only after the problem is familiar. The premise and tests remain available, but solution hints,
AI help, and solution lookup do not. Reconstruct from a blank file, explain correctness and
complexity, pass executable feedback, and solve a transfer variant.

Moving through these modes is progression, not cheating. Only the evidence label must stay honest.

## Canonical problem packets

Problem mechanics live in tracked packets under `harness/problems/` and bind to
`harness/problems/problem-packet-contract.v1.json`.

The first packet is Two Sum: `harness/problems/two-sum.v1.json`.

Read it as a self-contained exercise:

```bash
python scripts/study-problem.py render two-sum --mode guided
```

Create an editable Python attempt with the premise, example, checkpoints, feedback commands, and
starter function already present:

```bash
python scripts/study-problem.py render two-sum --mode guided --format comments --output two_sum_guided_attempt.py
```

A learner should be able to close the repository documentation and still know exactly what problem
they are solving.

## Two Sum: first guided loop

After reading the complete packet:

1. Restate the assignment in your own words.
2. Walk through the provided example and explain why its returned indices are correct.
3. Describe a slow but obviously correct pair-search strategy.
4. Write pseudocode for that slow strategy.
5. Implement `two_sum(nums, target)`.
6. Run executable feedback.

Do **not** require the optimized hash-map solution as the first successful rep. A correct brute-force
solution is useful evidence that the contract is understood.

## Executable feedback

Run:

```bash
python scripts/study-problem.py check two-sum two_sum_guided_attempt.py
```

The checker does not reveal a solution. It reports concrete failures such as a missing function,
Python exception, invalid result shape, same-index reuse, out-of-range indices, wrong sum, or input
mutation. A passing guided attempt proves tested behavior, not mastery.

## Graduated hints

Pull one hint at a time, make another attempt, then rerun the checker before escalating:

```bash
python scripts/study-problem.py hint two-sum --level 1
python scripts/study-problem.py hint two-sum --level 2
python scripts/study-problem.py hint two-sum --level 3
python scripts/study-problem.py hint two-sum --level 4
```

The reusable feedback doctrine remains `harness/skills/guided-feedback/SKILL.md` (`guided-feedback`).

## Documentation without asking an AI for the answer

When the algorithmic idea is understood but Python syntax is missing, run:

```bash
python scripts/study-problem.py docs two-sum
```

The packet supplies narrow documentation needs, suggested search wording, and official Python docs.
Searching for the exact Two Sum solution is solution lookup, not documentation lookup.

The reusable procedure remains `harness/skills/documentation-lookup/SKILL.md`
(`documentation-lookup`).

## Source-repository problem sets

When a repository such as SysAdminSuite becomes a source for exercises, do not expose a raw snippet
or vague questions as the assignment. Intake must first produce the same packet shape:

`source context -> premise -> inputs -> desired output -> constraints -> example -> checkpoints -> feedback`

The source repository remains authority for real behavior. StudySyndicate owns the pedagogical
restatement. Never copy secrets, client data, credentials, machine-specific identifiers, or
sensitive operational evidence into a study packet.

## Session evidence

Record the mode, problem/source, premise version, work completed before hints, highest hint level,
documentation consulted, checker evidence, explanation possible from memory, and next retrieval
target.
