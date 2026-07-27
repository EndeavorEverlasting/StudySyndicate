export type ActorKind =
  | 'learner'
  | 'source'
  | 'concept'
  | 'prompt'
  | 'response'
  | 'session'
  | 'attempt'
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
  | 'uses-media';

export type ComponentKind =
  | 'text-content'
  | 'media-ref'
  | 'pmp-map'
  | 'rubric'
  | 'schedule'
  | 'attempt-result'
  | 'provenance'
  | 'ui-state';

export type FactoredOwnerType = 'actor' | 'relationship';

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

export interface MediaRefData {
  storageKey: string;
  mimeType: string;
  caption?: string;
  durationMs?: number;
  width?: number;
  height?: number;
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

export interface ProvenanceData {
  sourceId?: string;
  importId?: string;
  author?: string;
  revision?: string;
}
