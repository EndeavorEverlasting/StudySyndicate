#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'governance validation: FAIL: %s\n' "$1" >&2
  exit 1
}

root="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "not inside a git repository"
cd "$root"

governance_file="AGENTS.md"
[[ -f "$governance_file" ]] || fail "$governance_file is missing"
git ls-files --error-unmatch "$governance_file" >/dev/null 2>&1 || fail "$governance_file is not tracked by git"

required_literals=(
  "# StudySyndicate Agent Governance"
  "single source of truth"
  "## Agent operating principles"
  "### Evidence before action"
  "### Floor before furniture"
  "### Bounded sprints with declared scope"
  "### One writer per branch"
  "### Reuse before replacing"
  "### No completion without proof"
  "### Learning evidence integrity"
  "Cascade/derived credit"
  "### Gameful learning experience"
  "Study activities should feel like games to the learner"
  "## Gameful study experience doctrine"
  "### Stable mechanics before gamification"
  "### Rewards are not mastery"
  "### Make failure playable"
  "### Honest game state"
  "### Agency, progression, and replayability"
  "### No dark patterns"
  "### Graceful fallback"
  "### Governance requirement for game-layer changes"
  "clear objectives"
  "immediate feedback"
  "visible progress"
  "progressive challenge"
  "Game systems must amplify learning mechanics rather than replace them."
  "Visual celebration cannot raise the proof level."
  "## Instruction precedence"
  "## Mandatory sprint declaration"
  "Proof ceiling"
  "## Completion standard"
  "## Forbidden behaviors"
  "## Governance enforcement"
  "bash scripts/validate-governance.sh"
  "## Actionable next command and next steps contract"
  "### NEXT COMMAND"
  "### NEXT STEPS"
  "Owner"
  "Dependency"
  "Artifact or proof"
  "Completion gate"
  "none; no safe actionable work remains"
  "## Final report contract"
)

for literal in "${required_literals[@]}"; do
  grep -Fq -- "$literal" "$governance_file" || fail "required doctrine is missing: $literal"
done

precedence_lines=(
  "1. Platform, security, legal, and repository-owner instructions."
  "2. This governance contract."
  "3. Task-specific prompts."
  "4. Generic defaults."
)

previous_line=0
for literal in "${precedence_lines[@]}"; do
  line="$(grep -nF -- "$literal" "$governance_file" | head -n1 | cut -d: -f1 || true)"
  [[ -n "$line" ]] || fail "instruction precedence entry is missing: $literal"
  (( line > previous_line )) || fail "instruction precedence is out of order at: $literal"
  previous_line="$line"
done

gameful_line="$(grep -nF -- "### Gameful learning experience" "$governance_file" | head -n1 | cut -d: -f1 || true)"
evidence_line="$(grep -nF -- "### Learning evidence integrity" "$governance_file" | head -n1 | cut -d: -f1 || true)"
precedence_heading_line="$(grep -nF -- "## Instruction precedence" "$governance_file" | head -n1 | cut -d: -f1 || true)"
[[ -n "$gameful_line" && -n "$evidence_line" && -n "$precedence_heading_line" ]] || fail "gameful doctrine ordering markers are missing"
(( gameful_line > evidence_line )) || fail "gameful doctrine must preserve learning evidence integrity before gamification"
(( gameful_line < precedence_heading_line )) || fail "gameful doctrine must remain inside the canonical operating-principles contract"

printf 'governance validation: PASS (%s tracked; required doctrine, gameful-learning contract, and precedence verified)\n' "$governance_file"
