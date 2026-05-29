export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface ApiEndpoint {
  path: string;
  method: string;
  description: string;
  inferred?: boolean;
  request_payload?: Record<string, any>;
  response_payload?: Record<string, any>;
}

export interface Microservice {
  id: string;
  name: string;
  description: string;
  domain: string;
  database: string;
  database_reasoning: string;
  boundary_justification?: string;
  inferred?: boolean;
  justified_fr_ids?: string[];
  apis: ApiEndpoint[];
  scaling_recommendations: string[];
  metadata?: Record<string, unknown>;
}

export interface Dependency {
  source: string;
  target: string;
  type: 'sync' | 'async';
  description: string;
}

export interface MetricScores {
  scalability: number;
  coupling: number;
  maintainability: number;
  fault_isolation: number;
  cohesion?: number;
}

export interface RequirementSentence {
  text: string;
  line: number;
  fr_ids: string[];
}

export interface TraceabilityRow {
  service_id: string;
  service_name: string;
  domain: string;
  confidence: number;
  matched_keywords: string[];
  requirement_sentences: RequirementSentence[];
  boundary_justification?: string;
  justified_fr_ids?: string[];
  inferred?: boolean;
}

export interface ClarificationQuestion {
  type: string;
  question: string;
  line: number;
  sentence: string;
  impact: string;
}

export interface AnalysisResult {
  project_id: string;
  raw_filename: string;
  raw_content_preview: string;
  microservices: Microservice[];
  dependencies: Dependency[];
  metrics: MetricScores;
  raw_feedback: string;
  analysis_metadata?: {
    traceability?: TraceabilityRow[];
    impact_map?: Record<string, string[]>;
    clarifications?: ClarificationQuestion[];
    flow_diagram?: string;
    [key: string]: unknown;
  };
}
