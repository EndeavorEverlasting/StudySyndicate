# Local Hook and Artifact Hygiene

StudySyndicate keeps generated/runtime evidence local unless a tracked contract explicitly owns it.

## Hook activation

Repository hooks are local and opt-in. This repository does not install or configure global hooks.

From the repository root:

```bash
git config core.hooksPath .githooks
```

Disable the repository-local hook path with:

```bash
git config --unset core.hooksPath
```

No hook installer exists at this floor. If one is introduced later, it must configure only the current repository.

## Pre-commit behavior

`.githooks/pre-commit` performs three bounded local checks:

1. `python scripts/check-staged-artifacts.py`
2. `python scripts/harness.py validate --level quick`
3. `git diff --cached --check`

The staged-artifact checker examines staged **path names only**. It does not read or print file contents.

It refuses obvious machine-local/generated categories such as:

- local study exports or runtime evidence;
- logs and crash dumps;
- local virtual environments/tool installs;
- save/session/process files;
- private-key/environment-style credential files;
- machine-local cache/junk paths.

When blocked, output is intentionally limited to the staged path plus remediation:

```text
[harness] refusing staged generated/runtime artifact: <path>
Move live/generated evidence back to ignored local output, or commit a sanitized fixture under an approved fixture/docs path.
```

## Sanitized fixtures

Generated-looking examples remain commit-friendly when they are intentionally sanitized and live under:

- `fixtures/`
- `tests/fixtures/`
- `docs/fixtures/`

Use `.fixture.` or `.example.` in the filename, for example:

```text
tests/fixtures/interview-session.fixture.log
docs/fixtures/crash-report.fixture.dmp
```

Credential-like files remain blocked even in fixture paths except the repository's explicit `.env.example` convention.

Normal source code, Markdown/docs, study contracts, and tracked harness reports are not blocked merely because they contain words such as `evidence`, `session`, or `artifact`.

## Safety boundary

The pre-commit hook does not launch the browser/app, run a learner/runtime adapter, or perform network activity. It retains the existing quick harness validation floor and staged whitespace check.

Live/generated evidence belongs in ignored local output. If an artifact needs to become durable repository authority, first create a sanitized fixture or register a tracked contract through the owning harness/artifact workflow instead of force-adding raw operator output.
