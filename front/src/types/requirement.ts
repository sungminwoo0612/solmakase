export type InputType = 'survey' | 'document' | 'chat' | 'expert';
export type DeploymentType = 'onprem' | 'cloud' | 'hybrid';
export type Scale = 'small' | 'medium' | 'large';

export interface RequirementCreate {
  user_id: string;
  input_type: InputType;
  service_type?: string;
  deployment_type?: DeploymentType;
  scale?: Scale;
  budget?: number;
  has_ops_team?: boolean;
  special_requirements?: string;
}

export interface RequirementResponse {
  id: string;
  user_id: string;
  input_type: InputType;
  service_type?: string;
  deployment_type?: DeploymentType;
  scale?: Scale;
  budget?: number;
  has_ops_team?: boolean;
  special_requirements?: string;
  structured_data?: Record<string, unknown>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessageCreate {
  requirement_id: string;
  message: string;
  role: 'user' | 'assistant';
}

export interface ChatMessageResponse {
  id: string;
  requirement_id: string;
  message: string;
  role: 'user' | 'assistant';
  created_at: string;
}

