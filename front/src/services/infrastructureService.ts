import apiClient from './api';
import type {
  InfrastructureCreate,
  InfrastructureResponse,
  IaCCodeResponse,
  IaCCodeModifyRequest,
} from '../types/infrastructure';

export const infrastructureService = {
  async createDesign(requirementId: string, designType: string, provider?: string): Promise<InfrastructureResponse> {
    const response = await apiClient.post<InfrastructureResponse>(
      `/infrastructure/design?requirement_id=${requirementId}&design_type=${designType}`,
      { provider }
    );
    return response.data;
  },

  async getInfrastructure(id: string): Promise<InfrastructureResponse> {
    const response = await apiClient.get<InfrastructureResponse>(`/infrastructure/${id}`);
    return response.data;
  },

  async getRequirementInfrastructures(requirementId: string): Promise<InfrastructureResponse[]> {
    const response = await apiClient.get<InfrastructureResponse[]>(
      `/infrastructure/requirement/${requirementId}`
    );
    return response.data;
  },

  async compareInfrastructures(requirementId: string): Promise<{
    onprem?: InfrastructureResponse;
    cloud?: InfrastructureResponse;
    comparison?: Record<string, unknown>;
  }> {
    const response = await apiClient.get(`/infrastructure/requirement/${requirementId}/compare`);
    return response.data;
  },

  async generateIaCCode(infrastructureId: string, iacTool: string = 'terraform'): Promise<IaCCodeResponse> {
    const response = await apiClient.post<IaCCodeResponse>(
      `/infrastructure/${infrastructureId}/generate-iac?iac_tool=${iacTool}`
    );
    return response.data;
  },

  async getIaCCode(infrastructureId: string): Promise<IaCCodeResponse> {
    const response = await apiClient.get<IaCCodeResponse>(`/infrastructure/${infrastructureId}/iac-code`);
    return response.data;
  },

  async getIaCCodeVersion(infrastructureId: string, version: number): Promise<IaCCodeResponse> {
    const response = await apiClient.get<IaCCodeResponse>(
      `/infrastructure/${infrastructureId}/iac-code/${version}`
    );
    return response.data;
  },

  async modifyIaCCode(infrastructureId: string, data: IaCCodeModifyRequest): Promise<IaCCodeResponse> {
    const response = await apiClient.post<IaCCodeResponse>(
      `/infrastructure/${infrastructureId}/iac-code/modify`,
      data
    );
    return response.data;
  },
};

