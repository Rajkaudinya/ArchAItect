// Types mirror the backend's `result` payload exactly.

export interface FunctionalArea {
  name: string;
  description: string;
  capabilities: string[];
}

export interface Service {
  id: string;
  name: string;
  responsibility: string;
  bounded_context: string;
  owns_entities: string[];
  key_apis: string[];
  data_store: string;
  rationale: string;
}

export interface Edge {
  from: string;
  to: string;
  type: "sync" | "async";
  protocol: string;
  reason: string;
}

export interface CompetitorService {
  name: string;
  purpose: string;
  source_hint: string;
}

export interface Competitor {
  competitor: string;
  why_relevant: string;
  known_services: CompetitorService[];
  insights: string[];
}

export interface Architecture {
  app_type: string;
  summary: string;
  actors: string[];
  functional_areas: FunctionalArea[];
  services: Service[];
  edges: Edge[];
  shared_concerns: string[];
  competitor: Competitor;
  preprocess?: {
    original_chars: number;
    digest_chars: number;
    compressed: boolean;
  };
}

// One SSE event from the pipeline.
export interface StepEvent {
  step: string;
  label?: string;
  status: "running" | "done" | "complete" | "error";
  data?: unknown;
  message?: string;
}

export const PIPELINE_STEPS: { key: string; label: string }[] = [
  { key: "domain", label: "Domain Extraction" },
  { key: "decompose", label: "Service Decomposition" },
  { key: "dependencies", label: "Dependency Mapping" },
  { key: "competitor", label: "Competitor Intel" },
  { key: "synthesis", label: "Synthesis" },
];
