import { useMemo, useState, type ReactNode } from 'react'
import { PracticeModal } from './components/PracticeModal'
import { practiceTargets } from './practice/catalog'
import { normalizeHostFailure, unavailableOutcome } from './practice/execution'
import { getLanguage, workbenchSpec } from './practice/registry'
import type { ExecutionOutcome, PanelId, PracticeSession } from './practice/types'
import './styles.css'

const initialSession: PracticeSession = {
  targetId: 'two-sum',
  facetId: 'understand',
  languageId: 'python',
  mode: 'guided',
}

const initialOutcome: ExecutionOutcome = {
  status: 'not-run',
  runnerId: 'none',
  summary: 'No feedback requested yet.',
  detail: 'Read the premise, make an attempt, then use the capability shown for this language.',
  recoverable: true,
}

export default function App() {
  const [session, setSession] = useState(initialSession)
  const [modalOpen, setModalOpen] = useState(false)
  const [panelOrder, setPanelOrder] = useState<PanelId[]>([...workbenchSpec.panelLayout.defaultOrder])
  const [draggedPanel, setDraggedPanel] = useState<PanelId | null>(null)
  const [draft, setDraft] = useState(() => practiceTargets[0]?.starterByLanguage?.python ?? '')
  const [outcome, setOutcome] = useState<ExecutionOutcome>(initialOutcome)

  const target = useMemo(
    () => practiceTargets.find((item) => item.id === session.targetId) ?? practiceTargets[0],
    [session.targetId],
  )
  const language = getLanguage(session.languageId)
  const facet = workbenchSpec.facets.find((item) => item.id === session.facetId) ?? workbenchSpec.facets[0]
  const externalCommand =
    target.id === 'two-sum' && language.id === 'python'
      ? 'python scripts/study-problem.py check two-sum PATH_TO_ATTEMPT.py'
      : language.id === 'sql'
        ? 'python scripts/sql-runner.py PATH_TO_ATTEMPT.sql'
        : null
  const externalCommandLabel = language.id === 'sql' ? 'Copy SQL runner' : 'Copy Python checker'

  const startSession = (next: PracticeSession) => {
    const nextTarget = practiceTargets.find((item) => item.id === next.targetId) ?? practiceTargets[0]
    const starter = nextTarget.starterByLanguage?.[next.languageId] ?? ''
    setSession(next)
    setDraft(starter)
    setOutcome(initialOutcome)
    setModalOpen(false)
  }

  const dropPanel = (targetPanel: PanelId) => {
    if (!draggedPanel || draggedPanel === targetPanel) return
    setPanelOrder((current) => {
      const without = current.filter((panel) => panel !== draggedPanel)
      const index = without.indexOf(targetPanel)
      without.splice(index, 0, draggedPanel)
      return without
    })
    setDraggedPanel(null)
  }

  const requestFeedback = () => {
    setOutcome(unavailableOutcome(language))
  }

  const copyExternalCommand = async () => {
    if (!externalCommand) return
    try {
      if (!navigator.clipboard) throw new Error('Clipboard API is unavailable in this browser context.')
      await navigator.clipboard.writeText(externalCommand)
      setOutcome({
        status: 'unsupported',
        runnerId: language.runner.id,
        summary: `${language.label} external runner command copied.`,
        detail: externalCommand,
        recoverable: true,
      })
    } catch (error) {
      setOutcome(normalizeHostFailure('browser-clipboard', error))
    }
  }

  const downloadDraft = () => {
    const extension: Record<string, string> = { python: 'py', rust: 'rs', sql: 'sql', c: 'c', javascript: 'js', typescript: 'ts', java: 'java', lua: 'lua' }
    try {
      const blob = new Blob([draft], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `${target.id}-attempt.${extension[language.id] ?? 'txt'}`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (error) {
      setOutcome(normalizeHostFailure('browser-download', error))
    }
  }

  const panelMap: Record<PanelId, ReactNode> = {
    premise: (
      <section className="panel premise-panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Premise first</span><h2>{target.title}</h2></div>
          <span className={`readiness ${target.readiness}`}>{target.readiness}</span>
        </div>
        <p className="premise-copy">{target.premise}</p>
        <div className="context-block"><strong>Context</strong><span>{target.context}</span></div>
        {target.example && <div className="example-block"><strong>Example</strong><code>{target.example}</code></div>}
        <div className="source-line">Authority · <code>{target.sourceAuthority}</code></div>
      </section>
    ),
    workspace: (
      <section className="panel workspace-panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Workspace</span><h2>{language.label} · {facet.label}</h2></div>
          <span className="runner-chip">{language.runner.status}</span>
        </div>
        <p className="facet-goal">{facet.goal}</p>
        <textarea
          className="code-editor"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          spellCheck={false}
          aria-label={`${language.label} practice editor`}
          placeholder="Write your attempt here. The editor intentionally remains usable as plain text when richer tooling is unavailable."
        />
        <div className="workspace-actions">
          <button type="button" className="primary-button" onClick={requestFeedback}>Check capability</button>
          <button type="button" className="secondary-button" onClick={downloadDraft}>Download attempt</button>
          {externalCommand && (
            <button type="button" className="secondary-button" onClick={copyExternalCommand}>{externalCommandLabel}</button>
          )}
        </div>
      </section>
    ),
    feedback: (
      <section className="panel feedback-panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Host-safe feedback</span><h2>{outcome.status}</h2></div>
          <span className="runner-chip">{outcome.runnerId}</span>
        </div>
        <p className="feedback-summary">{outcome.summary}</p>
        <p className="feedback-detail">{outcome.detail}</p>
        <div className="boundary-card">
          <strong>Execution boundary</strong>
          <span>{workbenchSpec.executionBoundary.principle}</span>
          <small>{language.runner.exceptionModel}</small>
        </div>
      </section>
    ),
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">SS</div>
          <div><span className="eyebrow">StudySyndicate</span><h1>Practice Workbench</h1></div>
        </div>
        <div className="topbar-actions">
          <span className="status-pill">{session.mode}</span>
          <button className="primary-button" type="button" onClick={() => setModalOpen(true)}>Configure session</button>
        </div>
      </header>

      <section className="session-strip" aria-label="Current practice session">
        <div><span>Target</span><strong>{target.title}</strong></div>
        <div><span>Facet</span><strong>{facet.label}</strong></div>
        <div><span>Language</span><strong>{language.label}</strong></div>
        <div><span>Runner</span><strong>{language.runner.kind}</strong></div>
      </section>

      <div className="workbench-intro">
        <div>
          <span className="eyebrow">Arrange your study surface</span>
          <h2>Premise, attempt, feedback — in the order that works for this rep.</h2>
        </div>
        <p>Drag panels to reorder them. The harness keeps the source, study mode, and runner capability authoritative.</p>
      </div>

      <section className="panel-grid" aria-label="Draggable practice panels">
        {panelOrder.map((panelId) => (
          <div
            className="panel-shell"
            key={panelId}
            draggable
            onDragStart={() => setDraggedPanel(panelId)}
            onDragOver={(event) => event.preventDefault()}
            onDrop={() => dropPanel(panelId)}
          >
            <div className="drag-handle" aria-hidden="true">⠿ drag</div>
            {panelMap[panelId]}
          </div>
        ))}
      </section>

      <PracticeModal
        open={modalOpen}
        targets={practiceTargets}
        current={session}
        onClose={() => setModalOpen(false)}
        onStart={startSession}
      />
    </main>
  )
}
