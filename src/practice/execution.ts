import type { ExecutionOutcome, LanguageCapability } from './types'

export function normalizeHostFailure(runnerId: string, error: unknown): ExecutionOutcome {
  const detail = error instanceof Error ? `${error.name}: ${error.message}` : String(error)
  return {
    status: 'host-error',
    runnerId,
    summary: 'The runner failed, but the study shell is still available.',
    detail,
    recoverable: true,
  }
}

export function unavailableOutcome(language: LanguageCapability): ExecutionOutcome {
  const external = language.runner.status === 'external-host-available'
  return {
    status: 'unsupported',
    runnerId: language.runner.id,
    summary: external
      ? `${language.label} feedback is available through an external host adapter.`
      : `${language.label} execution is capability-gated and not wired into the browser yet.`,
    detail: `${language.runner.kind}: ${language.runner.exceptionModel}`,
    recoverable: true,
  }
}
