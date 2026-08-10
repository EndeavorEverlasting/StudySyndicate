export type StudyMode = 'guided' | 'docs-assisted' | 'mastery'
export type PracticeFacetId = 'understand' | 'implement' | 'test' | 'explain' | 'docs'
export type RunnerStatus = 'external-host-available' | 'available-in-browser' | 'planned' | 'unavailable'
export type ExecutionStatus =
  | 'not-run'
  | 'passed'
  | 'failed'
  | 'compile-error'
  | 'runtime-error'
  | 'timeout'
  | 'unsupported'
  | 'host-error'

export interface RunnerCapability {
  id: string
  kind: string
  status: RunnerStatus
  exceptionModel: string
}

export interface LanguageCapability {
  id: string
  label: string
  editorMode: string
  runner: RunnerCapability
}

export interface PracticeFacet {
  id: PracticeFacetId
  label: string
  goal: string
}

export interface PracticeWorkbenchSpec {
  schema: string
  purpose: string
  facets: PracticeFacet[]
  studyModes: StudyMode[]
  executionBoundary: {
    principle: string
    normalizedStatuses: ExecutionStatus[]
    hostResponsibility: string
  }
  languages: LanguageCapability[]
  panelLayout: {
    defaultOrder: PanelId[]
    draggable: boolean
    requiredPanels: PanelId[]
  }
}

export type PanelId = 'premise' | 'workspace' | 'feedback'

export interface PracticeTarget {
  id: string
  title: string
  track: string
  sourceAuthority: string
  readiness: 'premise-first-packet' | 'exercise-catalog'
  premise: string
  context: string
  example?: string
  languages: string[]
  starterByLanguage?: Record<string, string>
}

export interface PracticeSession {
  targetId: string
  facetId: PracticeFacetId
  languageId: string
  mode: StudyMode
}

export interface ExecutionOutcome {
  status: ExecutionStatus
  runnerId: string
  summary: string
  detail: string
  recoverable: boolean
}
