# Guided Study Workflow

Use this when the learner is staring at a blank file and does not know how to begin.

## The three modes

### Guided

Use this first when the task feels daunting. Hints, examples, decomposition, documentation, and
feedback are allowed. The goal is to create a mental model and a first successful loop.

### Docs-assisted

Attempt from memory first, then use official documentation for syntax/API facts. Record exactly
what was looked up. Do not search for the exact challenge solution.

### Mastery

Use only after the problem is familiar. Start from a blank file with no AI and no solution lookup,
explain the invariant and complexity, pass the harness, and solve a transfer variant.

Moving through these modes is progression, not cheating. Only the label must stay honest.

## Two Sum: where to begin

Do **not** begin by trying to remember the final hash-map solution.

### Step 1 — write the contract in plain English

Answer on paper or in comments:

- What comes in?
- What must come out?
- Are values or indices required?
- Can the same index be used twice?
- What does the problem guarantee about solutions?

### Step 2 — hand-simulate one tiny example

Use:

```text
nums = [2, 7, 11, 15]
target = 9
```

Ask: if you stand on `2`, what other value would complete `9`?

Write the arithmetic explicitly:

```text
9 - 2 = 7
```

That subtraction is the complement idea.

### Step 3 — solve it the slow obvious way

Before optimizing, describe nested-loop brute force in words:

1. Pick one index.
2. Compare it with every later index.
3. If the values add to the target, return the two indices.

If coding is still too hard, write pseudocode first. A correct slow solution is a legitimate first
milestone because it proves you understand the contract.

### Step 4 — get feedback

Run the smallest executable test you have. If it fails, use
`harness/skills/guided-feedback/SKILL.md`. Do not inspect the known-good reference immediately.

### Step 5 — discover the optimization

Ask this question for every value `x`:

> What value would I need to have seen already so that `x + needed == target`?

Store previously seen values with their indices. Check for the needed value **before** storing the
current value so one element cannot match itself.

### Step 6 — explain before claiming mastery

Be able to say:

- brute force checks pairs and is `O(n^2)` time;
- the hash-map version trades `O(n)` extra space for expected `O(n)` time;
- the map stores `value -> earlier index`;
- lookup happens before insertion to avoid self-use.

Then use a blank file later for the `mastery` attempt.

## Documentation without asking an AI for the answer

When you know the concept but forget Python syntax, use the documentation skill:

`harness/skills/documentation-lookup/SKILL.md`

For Two Sum, legitimate syntax questions include:

- How do I create a dictionary?
- How do I test whether a key is in a dictionary?
- How do I enumerate a list with indices?
- How do I retrieve a dictionary value by key?

Searching for "Two Sum Python solution" is not documentation lookup; it is solution lookup.

## Session evidence

Record:

- mode
- problem/claim
- what you wrote before hints
- hint level reached
- documentation consulted
- failing/passing test
- explanation you can give from memory
- next retrieval target
