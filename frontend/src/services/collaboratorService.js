import apiClient from './api';

export const fetchUsers = async (params = {}) => {
  try {
    const response = await apiClient.get('/users/', { params: params });
    return response.data;
  } catch (error) {
    console.error("API Error fetching users:", error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const addCollaborator = async (taskId, userId) => {
  try {
    const response = await apiClient.post(`/tasks/${taskId}/collaborators/${userId}/`);
    return response.data;
  } catch (error) {
    console.error(`API Error adding collaborator ${userId} to task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const removeCollaborator = async (taskId, userId) => {
  try {
    await apiClient.delete(`/tasks/${taskId}/collaborators/${userId}/`);
    return true;
  } catch (error) {
    console.error(`API Error removing collaborator ${userId} from task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};