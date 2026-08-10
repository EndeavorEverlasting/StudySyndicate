# StudySyndicate Repository Work Ledger

**Start here when continuing repository work.**

The ledger is a coordination index, not implementation authority. It is intentionally rigid so a low-capability model or a hurried human does not have to infer what to do next.

## Three commands

Validate the ledger:

```bash
python scripts/validate-repo-ledger.py
```

Get the single highest-priority actionable frontier:

```bash
python scripts/get-repo-ledger-frontier.py
```

Get a copy/paste execution packet for a weak model or new chat:

```bash
python scripts/get-repo-ledger-frontier.py --prompt
```

Machine consumers can use:

```bash
python scripts/get-repo-ledger-frontier.py --json
```

## Route meanings

- `EXECUTE` — the selected task is `BOUNDED`. Claim it, mutate tracked files in its scope, and validate in the same sprint.
- `DECOMPOSE` — the selected task is `UNBOUNDED`. Create bounded child task blocks before implementation.
- `BLOCKED` — the exact dependency/collision gate is authoritative until it changes.
- `OPERATOR` — the next gate needs a human-controlled action or protected runtime.
- `EMPTY` — no actionable task exists.

## Anti-rumination rule

Once the frontier returns `EXECUTE`, continuing to analyze other queue entries is not progress. Work only the selected task until it changes state, is blocked by an exact gate, or is complete.

Once the frontier returns `DECOMPOSE`, do not implement the parent. Split it into bounded children first.

## Authority and versioning

Portable compatibility is adopted from:

- owner: `EndeavorEverlasting/BlacksmithGuild`
- contract: `RepoLedgerInteroperability.v1`
- pin: `429237aa41d8712d71859865c9be407ca23d8580`

The `BOUNDED` / `UNBOUNDED` execution profile and compact frontier are a StudySyndicate-local strengthening inspired by the AgentSwitchboard execution-frontier pattern at exact commit `b090637be810b2b25c35a11c299b4f2d9cc90ca3`. That reference is not runtime authority and no remote validator is executed.

StudySyndicate owns:

- `.ai/WORK_QUEUE.md`
- `.ai/repository-work-ledger-adoption.json`
- `.ai/repository-work-ledger.policy.json`
- `scripts/repo_ledger.py`
- `scripts/validate-repo-ledger.py`
- `scripts/get-repo-ledger-frontier.py`
- the local tests and CI workflow

## Task-writing rule

Every task has explicit nonblank fields and a closed vocabulary. The validator rejects ambiguous headings, duplicate fields, invalid status/priority/work class, fake claimed owners, vague next actions, weak terminal proof, bad blocker gates, stale local references, duplicate task IDs, and illegal monolithic `UNBOUNDED` implementation states.

Do not create a second queue or copy another repository's task namespace.
