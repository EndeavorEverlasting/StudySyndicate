import workbenchJson from '../../harness/practice-workbench.v1.json'
import type { LanguageCapability, PracticeWorkbenchSpec } from './types'

export const workbenchSpec = workbenchJson as unknown as PracticeWorkbenchSpec

export function getLanguage(id: string): LanguageCapability {
  const language = workbenchSpec.languages.find((item) => item.id === id)
  if (!language) {
    throw new Error(`Unknown language capability: ${id}`)
  }
  return language
}
