import apiClient from './api';
import type { RequirementCreate, RequirementResponse, ChatMessageCreate, ChatMessageResponse } from '../types/requirement';

export const requirementService = {
  async createRequirement(data: RequirementCreate): Promise<RequirementResponse> {
    const response = await apiClient.post<RequirementResponse>('/requirements', data);
    return response.data;
  },

  async getRequirement(id: string): Promise<RequirementResponse> {
    const response = await apiClient.get<RequirementResponse>(`/requirements/${id}`);
    return response.data;
  },

  async getUserRequirements(userId: string): Promise<RequirementResponse[]> {
    const response = await apiClient.get<RequirementResponse[]>(`/requirements/user/${userId}`);
    return response.data;
  },

  async uploadDocument(requirementId: string, file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post(`/requirements/upload?requirement_id=${requirementId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async sendChatMessage(data: ChatMessageCreate): Promise<ChatMessageResponse> {
    const response = await apiClient.post<ChatMessageResponse>(`/requirements/${data.requirement_id}/chat`, data);
    return response.data;
  },

  async getChatHistory(requirementId: string): Promise<ChatMessageResponse[]> {
    const response = await apiClient.get<ChatMessageResponse[]>(`/requirements/${requirementId}/chat`);
    return response.data;
  },
};

