# Multimodal Media and Voice Nodes

Status: canonical reusable media contract for StudySyndicate.

StudySyndicate treats media as study data, not decoration. Audio, images, and video are
first-class reusable nodes with stable identifiers, integrity metadata, provenance, and
explicit relationships to the cards or concepts that use them.

The machine-readable companion is
[`content/media/multimodal-media-contract.v1.json`](../content/media/multimodal-media-contract.v1.json).
Portable bundle behavior is implemented by [`scripts/media-bundle.py`](../scripts/media-bundle.py)
and enforced by [`scripts/validate-multimodal-media.py`](../scripts/validate-multimodal-media.py).

## Design goals

1. A flashcard may be text-only, audio-first, visual-first, or deliberately multimodal.
2. Spoken explanations can be saved as durable files and reused by more than one card.
3. Generated voice is an importable media node with provenance, not an ephemeral playback side effect.
4. Meaningful images remain usable when the image cannot be seen by carrying alt text.
5. Spoken audio remains usable when sound is unavailable by carrying a transcript.
6. Full exports can include the binary files instead of preserving only broken references.
7. Import verifies asset integrity before study records are trusted.

This supports different modalities and study contexts without assigning a permanent
"learning style" identity to a learner. Preference and context are allowed to change over time.

## Factored media model

Do not add audio bytes, image bytes, base64 payloads, or provider-specific voice objects
directly to a prompt, response, or concept.

A reusable media attachment is factored into:

1. a `media` actor — the durable node;
2. a `media-ref` component — the local binary asset metadata;
3. a `uses-media` relationship — the explicit link from a prompt, response, concept, or other actor;
4. a `media-usage` component on that relationship — how the media is used in this study context;
5. optional `text-content` and `provenance` components — transcript, alt/caption text, source, and revision history.

One media node may therefore serve as the spoken prompt for one card and the explanation for
another without duplicating the binary file.

## Media kinds

The first contract supports:

- `image`
- `audio`
- `video`

Text remains structured study data rather than a binary media kind.

## Media roles

Every `uses-media` relationship declares why the asset is present:

- `prompt` — primary stimulus before recall;
- `answer` — answer-side media;
- `explanation` — worked explanation or teaching narration;
- `mnemonic` — memory aid;
- `context` — supporting source/context.

The same media actor may have different roles in different relationships.

## Learning modes

A media usage may declare:

- `audio-first`
- `visual-first`
- `multimodal`
- `text-fallback`

These are presentation choices, not claims that a person has one immutable learning style.

## Voice nodes

A voice node is an `audio` media actor used for spoken study content.

Supported origins are:

- `recorded` — captured from a person;
- `generated` — synthesized from text;
- `imported` — brought in from an existing file.

For spoken audio:

- `speech` is true;
- `language` is required;
- a transcript is required;
- the binary asset is integrity-addressed with SHA-256 and byte length.

Generated speech additionally preserves reproducibility metadata such as the generator name,
model when known, a human-readable voice label when useful, and the SHA-256 of the source
transcript. Credentials, API keys, authorization headers, or provider secrets are never stored
in media metadata.

The transcript is study content in its own right. It can be rendered as a fallback, searched,
used to regenerate audio later, or compared during import.

## Visual nodes

Meaningful images carry alt text. Decorative images may explicitly set `decorative: true` and
omit alt text.

Image dimensions are metadata, not identity. The SHA-256 identifies the binary payload for
integrity and deduplication; the media actor id identifies the study node.

## Asset metadata

A `media-ref` component carries the durable storage contract:

- `assetId`
- `mediaKind`
- `storageKey`
- `mimeType`
- `sha256`
- `byteLength`
- `origin`

Useful optional metadata includes:

- `originalFileName`
- `language`
- `durationMs`
- `width`
- `height`
- `transcriptComponentId`
- `altText`
- `decorative`
- generated voice metadata

Remote URLs may be provenance or acquisition hints, but they are not the durable source of
truth for a saved StudySyndicate media node.

## Media usage metadata

A `media-usage` component carries presentation context:

- required `role`
- required `learningMode`
- optional `sequence`
- optional `autoplay`
- optional `startMs` / `endMs`
- optional `playbackRate`

`autoplay` defaults to false. A future UI may expose user preferences, but the stored asset is
independent of any one presentation choice.

## Portable media bundle

There are two complementary export artifacts.

### Structured JSON

`study.json` contains the structured study dataset: actors, relationships, components,
provenance, media metadata, and stable references. It does **not** embed binary image/audio/video
payloads.

### Full media bundle

A full portable export adds the binary files:

```text
manifest.json
study.json
assets/
  <sha256>.mp3
  <sha256>.png
  <sha256>.mp4
```

The transport may be a directory or a ZIP file. `manifest.json` uses the schema
`study-syndicate/media-bundle/v1`.

Assets are content-addressed as:

`assets/<sha256><lowercase-extension>`

Every manifest entry stores both `sha256` and `byteLength`.

Authority is intentionally split to prevent drift:

- `study.json` owns study semantics: actors, relationships, components, transcripts, alt text,
  media roles, and learning modes;
- `manifest.json` owns transport facts: bundle identity, asset path, MIME type, SHA-256, byte
  length, binary origin, accessibility-text hashes, and generated-voice provenance.

The manifest may mirror hashes of transcript/alt text for integrity, but it does not become a
second source of truth for the text itself or for how a card uses the media.

## Import rules

An importer must:

1. parse `study.json`;
2. validate the bundle manifest schema;
3. reject path traversal;
4. verify every binary file's SHA-256 and byte length;
5. fail when a required binary asset is missing;
6. deduplicate identical binary assets by SHA-256;
7. preserve stable media-node ids even when assets deduplicate;
8. reconstruct `uses-media` relationships and `media-usage` components from structured data.

Import must not silently replace an integrity mismatch with a remote download.

## Bundle tool

The repository includes a transport-level utility:

```bash
python scripts/media-bundle.py pack \
  --descriptor path/to/media-source.json \
  --assets-root path/to/assets \
  --study-json path/to/study.json \
  --output path/to/study-media.zip

python scripts/media-bundle.py validate path/to/study-media.zip
```

The source descriptor schema is `study-syndicate/media-bundle-source/v1`. The pack command
hashes and content-addresses the supplied files, writes `manifest.json`, includes `study.json`,
and refuses invalid speech/image accessibility metadata at pack time. Semantic media usage
remains authoritative in `study.json`; the manifest contains transport/integrity facts only.
The validate command rechecks the binary bundle before import.

This utility proves the portable file contract independently of the future browser UI. It does
not claim to decode codecs or perform speech synthesis.

## Example voice attachment

Conceptually:

```text
prompt actor
  └─ uses-media relationship (role=prompt, learningMode=audio-first)
       └─ media actor: "SQL HAVING explanation"
            ├─ media-ref: audio/mpeg, sha256, byteLength, local storage key
            ├─ text-content: transcript
            └─ provenance: generated/recorded/imported origin
```

A response can point to the same media actor with a second `uses-media` relationship and a
different role.

## Generation boundary

StudySyndicate may use available text/data to generate a voice asset, diagram, or image, but the
result becomes durable only after it is saved as a media node with integrity and provenance.

The repository contract separates:

- **generation** — how the asset was created;
- **storage** — where the binary is saved locally;
- **usage** — how a specific card presents it;
- **portability** — how the asset survives export/import.

This keeps future speech/image providers replaceable.

## Acceptance contract

The media floor is proven when:

1. image, audio, and video are reusable media actors rather than nested blobs;
2. spoken audio can preserve transcript, language, origin, integrity metadata, and generated-voice provenance;
3. media usage has an explicit role and learning mode;
4. a full bundle carries `study.json`, `manifest.json`, and integrity-addressed binary assets;
5. bundle validation rejects missing or corrupted files;
6. duplicate binaries can deduplicate by SHA-256 without collapsing distinct media-node ids;
7. spoken audio requires a transcript and meaningful images require alt text unless decorative.

## Validation

Run:

```bash
python scripts/validate-multimodal-media.py
python scripts/test-media-bundle.py
python scripts/validate-pmp-doctrine.py
```
