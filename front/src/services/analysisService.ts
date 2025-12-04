import apiClient from './api';
import type { AnalysisResponse } from '../types/analysis';

export const analysisService = {
  async analyzeRequirement(requirementId: string): Promise<AnalysisResponse> {
    const response = await apiClient.post<AnalysisResponse>(`/analysis/${requirementId}`);
    return response.data;
  },

  async getAnalysisResult(requirementId: string): Promise<AnalysisResponse> {
    const response = await apiClient.get<AnalysisResponse>(`/analysis/${requirementId}`);
    return response.data;
  },
};

