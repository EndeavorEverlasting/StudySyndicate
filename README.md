# StudySyndicate

Local-first PMP study app for multimedia flashcards, recall drills, weak-area tracking, and adaptive practice.

## Purpose

StudySyndicate helps PMP candidates build their own study system instead of relying on rigid flashcard tools. It supports text, image, audio, and video-based cards, tracks weak areas, and recommends targeted practice based on review history.

## Core Features

- Local-first storage
- PMP domain and competency mapping
- Multimedia flashcards
- Scenario-based exercises
- Free recall with rubric-based scoring
- Weak-area dashboard
- Spaced repetition scheduling
- Import/export support

## MVP Stack

- Vite
- React
- TypeScript
- Dexie.js
- IndexedDB
- ts-fsrs

## Storage Model

Primary data should use IndexedDB through Dexie.js. Browser localStorage should only be used for lightweight preferences.

## UI Principles

Use AxTask-inspired product principles when the app shell is scaffolded later:

- Keep primary actions obvious and close to the user's current study context.
- Favor calm, task-oriented screens over decorative chrome.
- Use compact dashboards that expose progress, weak areas, and next actions without requiring navigation.
- Make local-first state visible: import, export, backup, and sync status should be easy to find.
- Design empty states as setup guides so the first study loop is clear.

## Repository Hygiene

This repository is intentionally light until the app is scaffolded. Before adding a framework, keep the default branch clean and avoid committing generated artifacts, dependency folders, local environment files, or editor-specific state.

## License

MIT
