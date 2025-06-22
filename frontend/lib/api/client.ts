import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteurs pour auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API Methods
export const mangaAPI = {
  // Projects
  createProject: (data: CreateProjectDTO) => 
    apiClient.post('/projects', data),
  
  getProject: (id: string) => 
    apiClient.get(`/projects/${id}`),
  
  // Generation
  startGeneration: (projectId: string) => 
    apiClient.post(`/generation/start/${projectId}`),
  
  regeneratePanel: (panelId: string, modifications: any) =>
    apiClient.post(`/generation/regenerate/panel/${panelId}`, modifications),
  
  // Characters
  createCharacter: (projectId: string, data: CreateCharacterDTO) =>
    apiClient.post(`/characters/${projectId}`, data),
  
  trainCharacterLora: (characterId: string) =>
    apiClient.post(`/characters/${characterId}/train`),
  
  // Export
  exportPDF: (projectId: string, options: ExportOptions) =>
    apiClient.post(`/export/${projectId}/pdf`, options),
  
  exportWebtoon: (projectId: string) =>
    apiClient.post(`/export/${projectId}/webtoon`),
};
