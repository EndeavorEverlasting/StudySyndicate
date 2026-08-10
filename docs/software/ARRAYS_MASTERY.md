# Arrays and Algorithms Mastery Contract

This is the canonical StudySyndicate contract for building **defensible arrays-and-algorithms fluency**. The first gate is Two Sum because it forces a complete move from brute-force search to an explicit invariant, a lookup structure, edge-case reasoning, and complexity defense.

Repository reference code is study material. It is **not** proof that the learner personally mastered the problem. Personal proof begins when the learner can reconstruct the solution from a blank file without AI assistance, explain it, pass the harness, and transfer the pattern.

## Claim-defense doctrine

Use the same public-claim states as the software-foundations pack:

`exposed -> practicing -> defensible`

A problem is `defensible` only when all of these are true:

1. the input/output contract can be stated from memory;
2. a correct baseline can be reconstructed;
3. the optimization can be derived and implemented from a blank file without AI assistance;
4. the algorithm's invariant can be explained in ordinary language;
5. time and space complexity can be defended;
6. edge cases pass an executable harness;
7. a transfer exercise using the same pattern can be solved.

AI may explain, critique, generate additional tests, or compare alternatives **after** the learner attempts reconstruction. An assisted-study commit must never be presented as if it were proof of unaided mastery.

## Two Sum front to back

### Contract

Given an integer sequence and a target, return two **distinct indices** whose values sum to the target. The repository reference implementation raises `ValueError` when no solution exists so failure behavior is explicit, even though some interview versions guarantee a solution.

### Baseline: nested loops

Start with the version that is easiest to prove correct:

- choose a `left` index;
- compare it with every later `right` index;
- return when the two values sum to the target;
- begin `right` at `left + 1` so the same index is never reused.

Complexity: **O(n^2)** time and **O(1)** auxiliary space.

The baseline matters. Optimization is much easier to reason about when you can name the repeated work you are removing.

### Optimized model: complements

For the current value `value`, the only useful partner is:

`complement = target - value`

Instead of rescanning the array for that complement, remember earlier values in a hash map from value to index.

The core invariant is:

> Before processing index `i`, `seen` contains values from earlier indices only.

That makes the sequence of operations important:

1. compute the complement;
2. check whether the complement is already in `seen`;
3. if it is, return the earlier index and the current index;
4. otherwise insert the current value and index.

**Lookup before insert** is the detail to know cold. It both prevents a value from reusing its own index and permits a duplicate-value solution such as `[3, 3]` for target `6`.

Average complexity: **O(n)** time and **O(n)** auxiliary space.

## Two Sum mastery gate

Two Sum is not complete when the reference implementation makes sense while reading it. It is complete when the learner can do all of the following without copying:

1. state the contract;
2. write the nested-loop version;
3. explain why `right` starts at `left + 1`;
4. derive `target - value` as the complement;
5. write the hash-map version from a blank file;
6. explain the `seen` invariant;
7. explain lookup-before-insert using `[3, 3]`;
8. defend O(n^2)/O(1) versus average O(n)/O(n);
9. pass the harness covering duplicates, negatives, zero, self-reuse, no solution, and input immutability;
10. solve a transfer variant using hash lookup or two pointers.

The canonical reference implementations are in `practice/arrays/two_sum.py`. The correctness harness is `tests/test_two_sum.py`.

Run:

```bash
python tests/test_two_sum.py
```

## The 45-minute transition session

This track is designed to fit the task-to-study transition instead of creating another planning ritual.

| Minutes | Action | Proof |
| --- | --- | --- |
| 0-5 | Closed-book contract and invariant recall | spoken or written recall |
| 5-15 | Write/explain the brute-force version | code + O(n^2) explanation |
| 15-35 | Blank-file hash-map reconstruction | working code, no AI |
| 35-40 | Run edge cases and repair | harness output |
| 40-45 | Record complexity, confusion, next rep | evidence-ledger row |

If the optimized reconstruction fails, that is still useful evidence. Mark the session `practicing`, record the exact confusion, and make that confusion the first retrieval target next time.

## Arrays roadmap

Progress in this order. Do not race to a harder label while an earlier invariant is still fuzzy.

### 1. Array mechanics and invariants

Master index versus value, boundaries, mutation versus copying, and complete linear scans. Be able to narrate state at each index.

### 2. Two Sum front to back

Baseline search -> complement model -> hash lookup -> edge cases -> complexity -> blank-file reconstruction -> transfer.

### 3. Membership, frequency, and lookup tables

Use sets and dictionaries to remove repeated searches. Practice duplicate detection and frequency counting. Always be able to say what each stored key/value means.

### 4. Running state and one-pass optimization

Learn running minimum, running maximum, current candidate, and best-so-far invariants. Representative drills include single-transaction stock profit and maximum contiguous-subarray reasoning.

### 5. Prefix, suffix, and cumulative structure

Precompute information that lets later work become O(1) or one-pass. Practice prefix sums, suffix state, range queries, and product-except-self reasoning.

### 6. Sorted arrays and two pointers

Maintain a left/right invariant, explain why each pointer movement is safe, and understand when sorting changes the complexity or destroys original indices.

### 7. Fixed and variable windows

Update a window by accounting for what enters and leaves rather than recomputing everything. Explain why total pointer movement stays linear when applicable.

### 8. Binary search over array structure

Practice monotonic predicates, inclusive and half-open bounds, off-by-one defense, and rotated-array reasoning.

### 9. Unfamiliar array problem capstone

For a problem you have not memorized:

1. restate the contract;
2. write a correct baseline;
3. name the repeated work;
4. classify the reusable pattern;
5. optimize;
6. add adversarial tests;
7. defend time/space complexity;
8. reconstruct the key idea without AI;
9. record a public-safe evidence packet.

## Freelancer proof packet

The point is not to claim “algorithm expert” after one problem. The point is to accumulate evidence that survives scrutiny.

For each defensible problem, retain only public-safe proof:

- problem name and contract;
- commit or artifact containing the implementation;
- executable test command and result;
- complexity explanation;
- whether the final reconstruction was `blank-file-no-ai`;
- one transfer exercise;
- current mastery state.

Do not include proprietary client data, secrets, employer code, or fabricated retrospective evidence.

## Evidence ledger

A study row should be cheap enough to write in the last five minutes of a session:

`date | problem | attemptMode | artifact | tests | explanation | confusion | nextRep | masteryState`

Valid attempt modes are:

- `assisted-study`
- `closed-book`
- `blank-file-no-ai`
- `transfer`

An `assisted-study` row can advance understanding but cannot by itself advance a problem to `defensible`.

## Machine-readable pack

The canonical roadmap, Two Sum invariants, exercises, session template, evidence fields, and acceptance contract live at:

`content/software/arrays-mastery.v1.json`

## Validation

Run both the structural validator and executable kata harness:

```bash
python scripts/validate-arrays-mastery.py
python tests/test_two_sum.py
```

The validator enforces schema identity, roadmap order, Two Sum phases and invariants, 45-minute session math, evidence-ledger fields, exercise references, acceptance criteria, required doctrine language, and the presence of the executable reference/harness files.
