import { useEffect, useMemo, useRef, useState } from 'react'
import { getLanguage, workbenchSpec } from '../practice/registry'
import type { PracticeSession, PracticeTarget, StudyMode } from '../practice/types'

interface PracticeModalProps {
  open: boolean
  targets: PracticeTarget[]
  current: PracticeSession
  onClose: () => void
  onStart: (session: PracticeSession) => void
}

export function PracticeModal({ open, targets, current, onClose, onStart }: PracticeModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const [draft, setDraft] = useState(current)

  useEffect(() => {
    if (open) setDraft(current)
  }, [open, current])

  const target = useMemo(
    () => targets.find((item) => item.id === draft.targetId) ?? targets[0],
    [draft.targetId, targets],
  )
  const languageOptions = target.languages.map(getLanguage)

  useEffect(() => {
    if (!target.languages.includes(draft.languageId)) {
      setDraft((value) => ({ ...value, languageId: target.languages[0] }))
    }
  }, [draft.languageId, target.languages])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    dialogRef.current?.focus()
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  const masteryBlocked = target.readiness !== 'premise-first-packet'
  const setMode = (mode: StudyMode) => {
    if (mode === 'mastery' && masteryBlocked) return
    setDraft((value) => ({ ...value, mode }))
  }

  return (
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="practice-modal-title" tabIndex={-1} ref={dialogRef}>
        <div className="modal-heading">
          <div>
            <span className="eyebrow">Session configuration</span>
            <h2 id="practice-modal-title">Choose what you are practicing</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close session modal">×</button>
        </div>

        <label className="field">
          <span>Study target</span>
          <select value={draft.targetId} onChange={(event) => setDraft((value) => ({ ...value, targetId: event.target.value }))}>
            {targets.map((item) => <option key={item.id} value={item.id}>{item.track} · {item.title}</option>)}
          </select>
        </label>

        <div className="modal-grid">
          <label className="field">
            <span>Facet</span>
            <select value={draft.facetId} onChange={(event) => setDraft((value) => ({ ...value, facetId: event.target.value as PracticeSession['facetId'] }))}>
              {workbenchSpec.facets.map((facet) => <option key={facet.id} value={facet.id}>{facet.label}</option>)}
            </select>
          </label>

          <label className="field">
            <span>Language / environment</span>
            <select value={draft.languageId} onChange={(event) => setDraft((value) => ({ ...value, languageId: event.target.value }))}>
              {languageOptions.map((language) => <option key={language.id} value={language.id}>{language.label} · {language.runner.status}</option>)}
            </select>
          </label>
        </div>

        <fieldset className="mode-picker">
          <legend>Study mode</legend>
          {workbenchSpec.studyModes.map((mode) => (
            <button
              type="button"
              key={mode}
              className={draft.mode === mode ? 'mode-button active' : 'mode-button'}
              disabled={mode === 'mastery' && masteryBlocked}
              onClick={() => setMode(mode)}
            >
              <strong>{mode}</strong>
              <span>{mode === 'guided' ? 'Hints + feedback allowed' : mode === 'docs-assisted' ? 'Official docs after first attempt' : 'No-AI reconstruction proof'}</span>
            </button>
          ))}
        </fieldset>

        {masteryBlocked && (
          <p className="notice">This catalog item is not yet a full premise-first packet, so the UI will not label it as a mastery session.</p>
        )}

        <div className="modal-actions">
          <button className="secondary-button" type="button" onClick={onClose}>Cancel</button>
          <button className="primary-button" type="button" onClick={() => onStart(draft)}>Start session</button>
        </div>
      </div>
    </div>
  )
}
