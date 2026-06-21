# StudySyndicate Sprint Handoff

## Current Sprint Outcome

The repository has been reset to a lightweight, builder-friendly baseline for the next feature sprint. It now includes the previously missing public-facing `README.md` and MIT `LICENSE` files, plus repository hygiene and project-definition files, without framework scaffolding or generated artifacts.

## Known Gaps

- No runnable application has been scaffolded yet.
- The factored actor/relationship/component model has initial TypeScript contracts, but it is not implemented in Dexie tables yet.
- No package manager lockfile exists yet because dependencies have not been installed.
- No CI workflow exists yet.
- No issue labels, milestone, GitHub repository settings, or branch protections were configured from this local environment.
- No AxTask source repository or design tokens were available locally; only AxTask-inspired UI principles are captured in the README for future implementation.
- Remote GitHub access could not be verified from this environment because `git ls-remote` to GitHub failed with a 403 CONNECT tunnel error.

## Risks

- If framework scaffolding is added before confirming repository settings, generated defaults may introduce unnecessary files or conventions.
- If PMP copyrighted material, paid-course notes, or personal study media are committed, repository visibility should be private.
- If the app stores large media directly in Git, the repo can become difficult to clone and review.
- If the project name changes from `StudySyndicate`, import paths, package names, and documentation will need coordinated updates.
- If IndexedDB schema versions are not planned early, future migrations can become fragile.

## Near-Term Targets

1. Confirm GitHub repository name is `StudySyndicate` unless the misspelling `StudySindicate` is intentional branding.
2. Configure GitHub settings:
   - Issues on
   - Projects on
   - Wiki off
   - Automatically delete head branches on
   - Squash merging on
   - Merge commits off
3. Create labels:
   - `mvp`
   - `storage`
   - `cards`
   - `exercises`
   - `weakness-tracking`
   - `pmp-content`
   - `media`
   - `import-export`
   - `bug`
   - `tech-debt`
4. Create milestone `MVP-001 Local Study Engine`.
5. Scaffold the app only after repo settings are confirmed.
6. Implement the factored domain model early: `actors`, `relationships`, and `components` should be first-class tables/types before feature-specific shortcuts are added.
7. Use Vite, React, TypeScript, Dexie.js, IndexedDB, and ts-fsrs for the MVP stack.
8. Keep localStorage limited to lightweight preferences.

## Output Paths and Files to Analyze Next

- `README.md` — project intent, MVP stack, storage rules, domain model pointer, UI principles, repository file map, and license link.
- `docs/DOMAIN_MODEL.md` — factored actor, relationship, and component abstraction to implement before app data grows.
- `src/domain/factored.ts` — initial TypeScript contracts for factored domain records and common component payloads.
- `.gitignore` — ignored dependency, build, environment, cache, and editor artifacts.
- `LICENSE` — MIT license text that GitHub should detect as the repository license.
- `docs/SPRINT_HANDOFF.md` — this handoff, including gaps, risks, targets, and next analysis paths.

## Copy/Paste Plan for Another AI Agent

You are taking over the StudySyndicate repository. Treat it as a local-first PMP study app and keep the repo clean, boring, and builder-friendly.

1. Start by running:
   - `git status --short --branch`
   - `git branch -vv`
   - `git remote -v`
   - `find .. -name AGENTS.md -print`
2. Read any applicable `AGENTS.md` files before editing.
3. Confirm the repo is named `StudySyndicate`, not `StudySindicate`, unless the altered spelling is intentional branding.
4. Verify the baseline files:
   - `README.md`
   - `.gitignore`
   - `LICENSE`
   - `docs/DOMAIN_MODEL.md`
   - `src/domain/factored.ts`
   - `docs/SPRINT_HANDOFF.md`
5. Do not add framework scaffolding until GitHub repository settings are confirmed.
6. If scaffolding the MVP, target:
   - Vite
   - React
   - TypeScript
   - Dexie.js
   - IndexedDB
   - ts-fsrs
7. Do not commit:
   - `node_modules/`
   - build output
   - coverage output
   - `.env` files
   - local editor folders
   - generated caches
8. Preserve local-first architecture:
   - IndexedDB through Dexie.js for primary data
   - first-class `actors`, `relationships`, and `components` tables/types
   - localStorage only for lightweight preferences
   - import/export as a first-class user safety feature
9. Use AxTask-inspired UI principles:
   - calm task-oriented screens
   - obvious primary actions
   - dashboard surfaces weak areas and next actions
   - setup-focused empty states
   - visible local-first backup/import/export status
10. Before finishing, run:
    - `git status --short --branch`
    - `git diff --check`
11. Commit changes with a conventional commit message.
12. Leave a final response that lists summary, tests/checks, known gaps, risks, targets, and files to analyze next.
