import apiClient from './api';

export const fetchTasks = async (params = {}) => {
  try {
    const response = await apiClient.get('/tasks/', { params: params });
    return response.data;
  } catch (error) {
    console.error("API Error fetching tasks:", error.response?.data || error.message);
    throw error;
  }
};

export const createTask = async (taskData) => {
    try {
        const response = await apiClient.post('/tasks/', taskData);
        return response.data;
    } catch (error) {
        console.error("API Error creating task:", error.response?.data || error.message);
        throw error.response?.data || error;
    }
};

export const updateTask = async (taskId, taskData) => {
     try {
        const response = await apiClient.patch(`/tasks/${taskId}/`, taskData);
        return response.data;
    } catch (error) {
        console.error(`API Error updating task ${taskId}:`, error.response?.data || error.message);
        throw error.response?.data || error;
    }
};

export const deleteTaskApi = async (taskId) => {
    try {
        await apiClient.delete(`/tasks/${taskId}/`);
        return true;
    } catch (error) {
        console.error(`API Error deleting task ${taskId}:`, error.response?.data || error.message);
        throw error.response?.data || error;
    }
};

export const fetchTaskHistory = async (taskId) => {
  try {
    const response = await apiClient.get(`/tasks/${taskId}/history/`);
    return response.data;
  } catch (error)
{
    console.error(`API Error fetching history for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const fetchTaskComments = async (taskId, params = {}) => {
  try {
    const response = await apiClient.get(`/tasks/${taskId}/comments/`, { params: params });
    return response.data;
  } catch (error) {
    console.error(`API Error fetching comments for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const addTaskComment = async (taskId, commentData) => {
  try {
    const response = await apiClient.post(`/tasks/${taskId}/comments/`, commentData);
    return response.data;
  } catch (error) {
    console.error(`API Error adding comment for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};