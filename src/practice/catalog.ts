import arraysJson from '../../content/software/arrays-mastery.v1.json'
import foundationsJson from '../../content/software/sql-rust-foundations.v1.json'
import twoSumJson from '../../harness/problems/two-sum.v1.json'
import type { PracticeTarget } from './types'

interface Exercise {
  id: string
  module: string
  prompt: string
  proof: string
}

interface Module {
  id: string
  name: string
}

interface FoundationTrack {
  id: string
  modules: Module[]
  exercises: Exercise[]
}

interface FoundationsPack {
  tracks: FoundationTrack[]
}

interface ArraysPack {
  roadmap: Array<{ id: string; name: string }>
  exercises: Exercise[]
}

const foundations = foundationsJson as unknown as FoundationsPack
const arrays = arraysJson as unknown as ArraysPack
const twoSum = twoSumJson as typeof twoSumJson
const algorithmLanguages = ['python', 'rust', 'c', 'javascript', 'typescript', 'java', 'lua']

const twoSumStarters: Record<string, string> = {
  python: `def two_sum(nums, target):
    # Start with a clear, slow solution.
    pass
`,
  rust: `fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    todo!("start with the slow pair search")
}
`,
  c: `#include <stddef.h>

/* Return success and write the two indices through out_left/out_right. */
int two_sum(const int *nums, size_t len, int target, size_t *out_left, size_t *out_right) {
    return 0;
}
`,
  javascript: `function twoSum(nums, target) {
  // Start with the slow pair search.
}
`,
  typescript: `function twoSum(nums: number[], target: number): [number, number] | null {
  // Start with the slow pair search.
  return null
}
`,
  java: `static int[] twoSum(int[] nums, int target) {
    // Start with the slow pair search.
    return null;
}
`,
  lua: `function two_sum(nums, target)
  -- Start with the slow pair search.
end
`,
}

const twoSumTarget: PracticeTarget = {
  id: 'two-sum',
  title: twoSum.title,
  track: 'Arrays / Algorithms',
  sourceAuthority: 'harness/problems/two-sum.v1.json',
  readiness: 'premise-first-packet',
  premise: twoSum.premise,
  context: `Inputs: ${twoSum.inputs.map((item) => item.name).join(', ')} • Output: ${twoSum.output}`,
  example: `${JSON.stringify(twoSum.example.nums)} + target ${twoSum.example.target} → ${JSON.stringify(twoSum.example.output)}. ${twoSum.example.explanation}`,
  languages: algorithmLanguages,
  starterByLanguage: twoSumStarters,
}

function foundationTargets(trackId: 'sql' | 'rust'): PracticeTarget[] {
  const track = foundations.tracks.find((item) => item.id === trackId)
  if (!track) return []
  const moduleNames = new Map(track.modules.map((item) => [item.id, item.name]))
  const starterByLanguage: Record<string, string> = trackId === 'sql'
    ? { sql: '-- Write the smallest query that satisfies the premise.\n' }
    : { rust: '// Write the smallest Rust program/function that satisfies the premise.\n' }

  return track.exercises.map((exercise) => ({
    id: exercise.id,
    title: `${exercise.id.toUpperCase()} · ${moduleNames.get(exercise.module) ?? exercise.module}`,
    track: trackId === 'sql' ? 'SQL Foundations' : 'Rust Foundations',
    sourceAuthority: `content/software/sql-rust-foundations.v1.json#${exercise.id}`,
    readiness: 'exercise-catalog',
    premise: exercise.prompt,
    context: `Expected evidence: ${exercise.proof}. This item comes from the foundations exercise catalog; the UI must not invent missing schema/runtime details.`,
    languages: [trackId],
    starterByLanguage,
  }))
}

function arrayTargets(): PracticeTarget[] {
  const moduleNames = new Map(arrays.roadmap.map((item) => [item.id, item.name]))
  return arrays.exercises.map((exercise) => ({
    id: exercise.id,
    title: `${exercise.id.toUpperCase()} · ${moduleNames.get(exercise.module) ?? exercise.module}`,
    track: 'Arrays Roadmap',
    sourceAuthority: `content/software/arrays-mastery.v1.json#${exercise.id}`,
    readiness: 'exercise-catalog',
    premise: exercise.prompt,
    context: `Expected evidence: ${exercise.proof}. Convert this catalog exercise to a full problem packet before labeling a rep mastery.`,
    languages: algorithmLanguages,
    starterByLanguage: Object.fromEntries(algorithmLanguages.map((language) => [language, twoSumStarters[language] ?? ''])),
  }))
}

export const practiceTargets: PracticeTarget[] = [
  twoSumTarget,
  ...arrayTargets(),
  ...foundationTargets('sql'),
  ...foundationTargets('rust'),
]
