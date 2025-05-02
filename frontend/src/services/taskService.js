import apiClient from './api';

export const fetchTasks = async () => {
  try {
    const response = await apiClient.get('/tasks/');
    return response.data;
  } catch (error) {
    console.error("API Error fetching tasks:", error);
    throw error;
  }
};

export const createTask = async (taskData) => {
    try {
        const response = await apiClient.post('/tasks/', taskData);
        return response.data;
    } catch (error) {
        console.error("API Error creating task:", error.response?.data || error);
        throw error;
    }
};

export const updateTask = async (taskId, taskData) => {
     try {
        const response = await apiClient.patch(`/tasks/${taskId}/`, taskData);
        return response.data;
    } catch (error) {
        console.error(`API Error updating task ${taskId}:`, error.response?.data || error);
        throw error;
    }
};