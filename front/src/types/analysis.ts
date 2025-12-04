export interface AnalysisResponse {
  requirement_id: string;
  analysis_data: Record<string, unknown>;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  created_at?: string;
}

