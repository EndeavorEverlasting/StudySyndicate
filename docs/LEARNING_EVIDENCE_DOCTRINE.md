# Learning Evidence and Partial-Credit Doctrine

## Purpose

StudySyndicate must preserve **what the learner actually demonstrated**, not reduce a learning event to a binary
right/wrong label. A failed final answer can still contain useful evidence: the learner may have reconstructed the
representation, applied part of the procedure, found a bug, explained a constraint, or discovered a new connection.

The canonical machine-readable scoring contract is
`content/learning/learning-evidence.v1.json`. The deterministic reference engine is
`scripts/learning-evidence.py`.

## The three core motions

Every durable learning system needs to recognize three motions that happen at different speeds:

1. **Construct** — synthesize or reconstruct the idea from memory.
2. **Apply** — use the idea against a concrete problem, input, tool, or environment.
3. **Discover** — create a useful question, connection, experiment, or inference that was not handed over as an answer.

StudySyndicate also records **Debug** and **Explain** because those motions expose knowledge that binary answer grading
usually throws away.

## Evidence before labels

A learning event is append-only evidence. Score demonstrated facets first; derive labels second.

- An incorrect result does not erase correct intermediate reasoning.
- A correct result does not prove that the learner can reconstruct or explain it.
- Hints, documentation, and AI assistance are recorded as provenance rather than hidden.
- Assistance may cap the strongest claim from a rep, but it does not turn real learner work into zero credit.
- Credit is not a compliment. It is a bounded statement about observed behavior.

## Assistance boundary

The contract defines explicit assistance bands. Unassisted and documentation-assisted work can emit a strong
single-rep mastery **signal** when the required facets are strong. Hint- or AI-assisted work cannot.

No single event may claim mastery. Mastery requires repeated direct evidence, at least one unassisted rep, required
facet quality, and transfer. An AI-generated answer is therefore source/scaffold material until the learner can
reconstruct and transfer the idea.

## Cascading events

Learning frequently exercises prerequisite or adjacent ideas. An event may explicitly declare those relationships.

The engine may propagate a bounded fraction of the event score as **cascade recognition** to those related concepts.
That recognition exists so the learner can see that the work was not wasted and so the scheduler can make better
practice decisions.

Cascade recognition:

- must identify the related concept explicitly;
- is capped by the contract's cascade factor and relation weight;
- is labeled as derived rather than direct evidence;
- never counts toward mastery;
- must not silently increase a resume/public skill claim.

## Acknowledgment without inflation

Acknowledgment should answer: *what did the learner actually do here?* It should not manufacture certainty or
self-esteem by declaring competence that was not observed.

The engine therefore emits:

- event credit;
- earned facets;
- the weakest next facet;
- assistance provenance;
- bounded cascade recognition;
- a plain-language acknowledgment band;
- an explicit mastery boundary.

This supports confidence through accumulated evidence rather than through ungrounded reassurance.

## AI behavior

Agents should prefer a sequence that creates learner evidence:

1. restate the complete premise;
2. ask for or preserve the learner's attempt;
3. identify demonstrated facets before exposing an answer;
4. offer the smallest useful hint, documentation target, or failing case;
5. record assistance used;
6. let the learner revise;
7. score the new evidence;
8. only expose a full reference answer when the workflow calls for it.

When an agent supplies code first, that output belongs to the source/scaffold side of the system. It does not become
learner evidence merely because it compiled.

## Engine boundaries

The current engine is intentionally deterministic and local. It does not use an LLM to decide credit. Humans or
future evaluators may produce facet-quality observations, but the transformation from those observations to credit,
caps, cascade recognition, and acknowledgment is reproducible.

Future adaptive engines may consume this contract for scheduling, UI, recommendations, and longitudinal analysis
without changing the meaning of the evidence.
