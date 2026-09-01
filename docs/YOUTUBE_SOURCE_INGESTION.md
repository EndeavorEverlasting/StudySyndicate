# YouTube Source Ingestion

StudySyndicate delegates live YouTube extraction to `yt-dlp`. The repository owns only input census, canonical source normalization, occurrence/completeness semantics, provenance, and JSON/CSV export.

## Supported inputs

- one YouTube playlist URL;
- one YouTube video/Short URL;
- multiple video URLs supplied in order;
- saved `yt-dlp` JSON through `--input-json` for deterministic/offline proof.

For multiple video URLs, tracking/share parameters such as `si=` do not create new video identity. The adapter extracts each unique video ID at most once, reuses one canonical video actor, and preserves every supplied occurrence and input position.

Unavailable/null collection slots remain tombstone occurrences. Completeness is reported as `COMPLETE`, `PARTIAL`, `EMPTY_CONFIRMED`, `EMPTY_UNPROVEN`, or `FAILED`. Playlist order prefers extractor `playlist_index`; encounter-order fallback is explicit. URL lists use `input_order`.

## Windows run sheet

Install the external extractor when needed:

```powershell
winget install --id yt-dlp.yt-dlp -e
```

Import a playlist:

```powershell
python scripts/source-ingest-youtube.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

Import a single video or Short:

```powershell
python scripts/source-ingest-youtube.py "https://youtu.be/VIDEO_ID"
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

Import multiple video URLs while preserving duplicates and order:

```powershell
python scripts/source-ingest-youtube.py `
  "https://youtu.be/VIDEO_ID_1" `
  "https://youtu.be/VIDEO_ID_2" `
  "https://youtu.be/VIDEO_ID_1?si=tracking-value"
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

Run deterministic fixture proof without network access:

```powershell
python scripts/source-ingest-youtube.py `
  --input-json tests/fixtures/yt-dlp-playlist.json `
  --extractor-version 2026.08.19 `
  --captured-at 2026-08-26T21:00:00Z `
  --output-dir local-study-exports `
  --basename fixture-proof
if ($LASTEXITCODE) { exit $LASTEXITCODE }

python scripts/validate-source-ingestion.py
if ($LASTEXITCODE) { exit $LASTEXITCODE }

python tests/test_youtube_source_ingestion.py
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

## Output and path safety

The repository-owned default output root remains ignored `local-study-exports/`; the standalone packet's generic `Outputs/` path is not a second repository authority.

Before any write, the adapter resolves generated JSON/CSV paths and protects the saved `--input-json` file plus the tracked contract and donor manifest from equal-path collisions. A rejected collision must leave the protected input byte-identical.

Canonical JSON remains the source of truth. CSV is derived from it with `utf-8-sig` encoding and a real UTF-8 BOM. String cells beginning with `=`, `+`, `-`, or `@` are prefixed with an apostrophe in CSV only; JSON values are unchanged.

## Proof ceiling

Offline fixture tests prove normalization, occurrence identity/order, completeness, path collision defense, UTF-8/BOM behavior, spreadsheet-safe CSV projection, donor pin enforcement, and CLI determinism. They do not prove current live YouTube behavior, private/authenticated access, or the workstation's installed `yt-dlp` version.
