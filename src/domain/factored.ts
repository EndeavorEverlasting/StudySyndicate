export type ActorKind =
  | 'learner'
  | 'source'
  | 'concept'
  | 'prompt'
  | 'response'
  | 'session'
  | 'attempt'
  | 'learning-event'
  | 'media';

export type RelationshipKind =
  | 'derived-from'
  | 'tests'
  | 'explains'
  | 'contains'
  | 'depends-on'
  | 'conflicts-with'
  | 'attempted-in'
  | 'answered-by'
  | 'evidences'
  | 'reinforces'
  | 'uses-media';

export type ComponentKind =
  | 'text-content'
  | 'source-ref'
  | 'media-ref'
  | 'media-usage'
  | 'pmp-map'
  | 'rubric'
  | 'schedule'
  | 'attempt-result'
  | 'learning-evidence'
  | 'acknowledgement'
  | 'provenance'
  | 'ui-state';

export type FactoredOwnerType = 'actor' | 'relationship';

export type MediaKind = 'image' | 'audio' | 'video';

export type MediaRole =
  | 'prompt'
  | 'answer'
  | 'explanation'
  | 'mnemonic'
  | 'context';

export type MediaLearningMode =
  | 'audio-first'
  | 'visual-first'
  | 'multimodal'
  | 'text-fallback';

export type MediaOrigin = 'recorded' | 'generated' | 'imported';

export type LearningFacet = 'construct' | 'apply' | 'debug' | 'explain' | 'discover';
export type AssistanceBand = 'none' | 'docs' | 'hint' | 'ai-scaffold' | 'ai-answer';

export interface TimestampedRecord {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface Actor extends TimestampedRecord {
  kind: ActorKind;
  label: string;
}

export interface Relationship extends TimestampedRecord {
  kind: RelationshipKind;
  fromActorId: string;
  toActorId: string;
  order?: number;
  weight?: number;
}

export interface Component<TData = unknown> extends TimestampedRecord {
  kind: ComponentKind;
  ownerType: FactoredOwnerType;
  ownerId: string;
  data: TData;
}

export interface TextContentData {
  format: 'markdown' | 'plain-text';
  body: string;
}

export interface SourceRefData {
  sourceKind: string;
  provider: string;
  locator: string;
  externalId: string;
  parentExternalId?: string;
  playlistIndex?: number;
  durationSeconds?: number;
  channelId?: string;
  thumbnailUrl?: string;
  uploadDate?: string;
  viewCount?: number;
  availability?: string;
}

export interface VoiceMetadata {
  generator: string;
  model?: string;
  label?: string;
  sourceTextSha256?: string;
}

export interface MediaRefData {
  assetId: string;
  mediaKind: MediaKind;
  storageKey: string;
  mimeType: string;
  sha256: string;
  byteLength: number;
  origin: MediaOrigin;
  originalFileName?: string;
  language?: string;
  durationMs?: number;
  width?: number;
  height?: number;
  speech?: boolean;
  transcriptComponentId?: string;
  altText?: string;
  decorative?: boolean;
  voice?: VoiceMetadata;
}

export interface MediaUsageData {
  role: MediaRole;
  learningMode: MediaLearningMode;
  sequence?: number;
  autoplay?: boolean;
  startMs?: number;
  endMs?: number;
  playbackRate?: number;
}

export interface PmpMapData {
  domains: string[];
  tasks: string[];
  processGroups?: string[];
  knowledgeAreas?: string[];
  competencies?: string[];
}

export interface RubricData {
  criteria: Array<{
    id: string;
    label: string;
    points: number;
  }>;
}

export interface ScheduleData {
  dueAt: string;
  stability?: number;
  difficulty?: number;
  lapses: number;
  lastReviewedAt?: string;
}

export interface AttemptResultData {
  grade: 'again' | 'hard' | 'good' | 'easy' | 'manual';
  confidence?: number;
  durationMs?: number;
  weakSignals?: string[];
  notes?: string;
}

export interface LearningEvidenceFacetData {
  facet: LearningFacet;
  quality: number;
  credit: number;
  note?: string;
}

export interface LearningEvidenceData {
  assistance: AssistanceBand;
  rawCredit: number;
  eventCredit: number;
  creditCap: number;
  earnedFacets: LearningEvidenceFacetData[];
  weakestFacet: { facet: LearningFacet; quality: number };
  eventMasterySignal: boolean;
  masteryClaimAllowed: false;
}

export interface AcknowledgementData {
  band: 'started' | 'traction' | 'substantial' | 'strong-rep';
  message: string;
  derived?: boolean;
}

export interface ProvenanceData {
  sourceId?: string;
  importId?: string;
  author?: string;
  revision?: string;
}
