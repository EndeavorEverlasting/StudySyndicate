# Skill: Repository Location Recovery

## Trigger

Use this skill when Git reports `not a git repository`, a terminal restart changed the current directory, a temporary worktree may be active, or an operator/agent is about to clone, install, create a worktree, or `cd` based on a remembered StudySyndicate path.

## Authority

`harness/canonical-paths.v1.json` is the path owner. `scripts/Resolve-StudySyndicateRepo.ps1` is the executable resolver. Do not maintain a second list of plausible roots in prompts, skills, launchers, or scripts.

Repository identity is `EndeavorEverlasting/StudySyndicate`.

## Procedure

1. Do not mutate, clean, clone, or create a worktree while location identity is unresolved.
2. Resolve the active tracked profile. On the Windows operator profile, obtain Desktop with `[Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)` and derive `Dev\StudySyndicate` from the contract. Never assume `%USERPROFILE%\Desktop` and never infer OneDrive redirection merely from an installed/running client.
3. Invoke `scripts/Resolve-StudySyndicateRepo.ps1` and record its `studysyndicate.path-input-receipt.v1`.
4. Require both canonical path identity and Git origin identity. Folder name alone is not proof.
5. Treat `CANONICAL + PROVED` as the only normal mutable development checkout state.
6. Treat another verified checkout as `NONCANONICAL + PRESERVE`; inspect status and unpushed/unique commits before any move or cleanup. Lower-precedence checkout evidence may expose drift but may not replace the tracked path contract.
7. For parallel writers, use the tracked sibling worktree root `<Desktop Known Folder>\Dev\StudySyndicate-worktrees`; do not create a second durable clone or put worktrees inside the canonical checkout.
8. Use `git -C <canonical-root> ...` or absolute script paths until the operator intentionally changes directory.
9. Run the quick harness after canonical resolution when repository work is about to begin.
10. Keep remote integration, local checkout currency, local-use currency, and real entrypoint proof separate.

## Required receipt

Record:

- platform and selected profile key;
- Desktop Known Folder when applicable;
- OneDrive state without fallback rewriting;
- canonical development/use/worktree paths;
- observed path and observed repository root;
- path classification/status;
- repository origin, branch, and exact HEAD when canonical proof exists;
- evidence sources and exact safe next action.

## Failure handling

`MISSING`, `CONFLICT`, `UNKNOWN`, or `NONCANONICAL + PRESERVE` is not permission to improvise another path. Stop with the canonical rule, observed evidence, and preservation action. Inventory existing copies before a clone is created.

Never `reset --hard`, `clean`, delete a worktree, or remove a checkout merely to make path state look tidy. Preserve dirty, unpushed, unique, or separately owned work.

## Reference

See `harness/canonical-paths.v1.json`, `harness/workflows/REPO_LOCATION_RECOVERY.md`, and `scripts/Resolve-StudySyndicateRepo.ps1`.
