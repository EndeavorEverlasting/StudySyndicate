# StudySyndicate Agent Governance

Status: canonical repository governance contract.

This file is the single source of truth for how writing agents operate in StudySyndicate. It applies from the repository root downward unless a higher-precedence instruction explicitly overrides it. Do not create a competing governance file.

## Agent operating principles

### Evidence before action
Inspect the repository, current branch, relevant open pull requests, existing contracts, validators, scripts, and recent changes before mutating files. Claims must be grounded in repository or runtime evidence.

### Floor before furniture
Establish the smallest correct foundation, contract, validation path, and failure behavior before adding polish, optional structure, or product expansion.

### Bounded sprints with declared scope
Every writing sprint must declare its lane, mission, owned scope, forbidden scope, expected artifacts, validation commands, and proof ceiling before mutation begins. Stay inside that boundary unless a higher-precedence instruction changes it.

### One writer per branch
Only one active writer may mutate a branch at a time. Parallel work must use separate branches or isolated worktrees. Do not overwrite, reset, or absorb separately owned dirty work.

### Reuse before replacing
Search for and reuse existing contracts, helpers, validators, scripts, naming conventions, manifests, registries, docs, and output patterns before inventing replacements. Repair canonical artifacts instead of creating duplicates.

### No completion without proof
Do not claim completion from intent, file creation, or inspection alone. Completion requires named changes, executed validation, a commit SHA, and reported push or pull-request state at the highest proof level actually reached.

## Instruction precedence

When instructions conflict, apply them in this order:

1. Platform, security, legal, and repository-owner instructions.
2. This governance contract.
3. Task-specific prompts.
4. Generic defaults.

Lower-precedence instructions must not weaken higher-precedence safety, scope, validation, or proof requirements.

## Mandatory sprint declaration

Before any writing sprint, state:

- **Repo and branch:** exact repository and active branch.
- **Lane and mission:** the workstream and concrete outcome.
- **Owned scope:** files, directories, systems, or artifacts that may be changed.
- **Forbidden scope:** adjacent work that must not be changed.
- **Expected artifacts:** exact files, reports, commits, pull requests, or runtime outputs expected.
- **Validation commands:** commands that will actually be run before completion is claimed.
- **Proof ceiling:** the highest evidence level reachable in the current environment.

Use the narrowest proof ceiling that is honest. Typical ceilings are:

- `repository-write`: files and commit can be proven, but remote checks cannot.
- `remote-ci`: pushed branch and remote checks can be proven.
- `merged`: required review/check gates and merge state can be proven.
- `runtime`: the changed behavior can be exercised in its intended runtime.
- `production`: production deployment and live verification are authorized and observable.

Never imply proof above the declared or actually reached ceiling.

## Completion standard

A task is complete only when all applicable items below are satisfied and reported:

1. Every created or modified file is named.
2. Required validation commands were actually run and their results are reported; assumed or skipped checks are explicitly identified.
3. A commit SHA containing the completed owned-scope work exists.
4. Push state and pull-request state are reported, including blockers when remote mutation or review is unavailable.
5. The final report gives one exact executable next command unless no safe actionable work remains.

If any required item is missing, report the task as incomplete at the proven ceiling rather than overstating completion.

## Forbidden behaviors

Agents must not:

- acknowledge a mutation request without performing authorized mutation when safe execution is available;
- stop at a plan when the owned implementation can be executed safely;
- substitute a summary, inventory, or status recap for required proof;
- claim tests, validation, deployment, merge, or completion without actually observing the evidence;
- expose, print, commit, copy, or solicit secrets, credentials, tokens, private keys, or sensitive authentication material;
- force-push, destructively clean, discard separately owned work, or rewrite unrelated history unless a higher-precedence instruction explicitly authorizes it;
- create duplicate governance contracts when this canonical file can be repaired.

## Governance enforcement

The canonical validator is:

```bash
bash scripts/validate-governance.sh
```

The validator must fail when this file is missing, untracked, or missing required governance clauses. Pull requests that change the governance surface must also pass `git diff --check` through the governance workflow.

A governance change is not proven merely because the Markdown renders or the validator script exists; the validator must execute successfully.

## Actionable next command and next steps contract

Final reports must advance the work into the next useful unproven state rather than merely restating status.

### NEXT COMMAND

Provide exactly one copy-paste command when safe executable work remains. The command must begin with the first executable action and, where applicable, must:

- set or resolve the repository location;
- fetch without force;
- verify the intended branch and exact commit;
- preserve dirty or separately owned work through an isolated worktree or another non-destructive mechanism;
- run the owning validator, build, launcher, or runtime proof command;
- resolve the canonical artifact from tracked repository authority rather than a guessed path;
- open or print the resulting artifact when useful;
- propagate every nonzero exit code.

For unmerged remote work, the next command must validate the exact remote branch/commit rather than silently switching to another revision.

When no artifact exists yet, the next action must create or repair the next owned artifact and prove it; inspection alone is not an implementation step.

When review, merge permission, credentials, a protected runtime, a technician workstation, or production access is the real blocker, name that blocker exactly and provide the command or operator action that advances that gate without claiming higher proof.

### NEXT STEPS

When more than one remaining step matters, list them in dependency order. Every step must name:

- **Owner** — the agent, reviewer, operator, technician, or other actor responsible.
- **Dependency** — the prerequisite state or artifact.
- **Action** — an exact command or concrete operator action.
- **Artifact or proof** — the file, log, check, review, runtime output, or state produced.
- **Completion gate** — the observable condition that proves the step is done.

Generic advice such as `test`, `review`, `merge`, `deploy`, `document`, `monitor`, `continue`, or `wait` is invalid without those specifics.

Use `none; no safe actionable work remains` only when all authorized work is complete, required validation actually ran, commit and push or pull-request state are reported, preserved-work or cleanup state is reported, and no safe unproven action remains.

## Final report contract

Serious repository work ends with:

- completed work and every important path changed;
- validation commands and observed results;
- skipped checks, gaps, blockers, and risks;
- commit SHA and git/pull-request state;
- preserved or separately owned work that was intentionally not modified;
- the exact next command;
- a copy-paste handoff prompt when another agent or chat is the next owner.
