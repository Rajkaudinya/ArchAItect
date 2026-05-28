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
}

export interface TraceabilityRow {
  service_id: string;
  service_name: string;
  domain: string;
  confidence: number;
  matched_keywords: string[];
  requirement_sentences: string[];
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
    [key: string]: unknown;
  };
}
