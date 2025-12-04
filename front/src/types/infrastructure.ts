export type DesignType = 'onprem' | 'cloud' | 'hybrid';

export interface InfrastructureCreate {
  requirement_id: string;
  design_type: DesignType;
  provider?: string;
}

export interface InfrastructureResponse {
  id: string;
  requirement_id: string;
  design_type: DesignType;
  provider?: string;
  architecture: Record<string, unknown>;
  cost_estimate?: Record<string, unknown>;
  plan_document?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface IaCCodeResponse {
  id: string;
  infrastructure_id: string;
  iac_tool: string;
  code: string;
  version: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface IaCCodeModifyRequest {
  prompt: string;
}

