// src/services/taskService.js
import apiClient from './api'; // Corrected path as per your confirmation

export const fetchTasks = async () => {
  try {
    const response = await apiClient.get('/tasks/');
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

export const deleteTaskApi = async (taskId) => { // <<< RENAMED EXPORT TO deleteTaskApi
    try {
        await apiClient.delete(`/tasks/${taskId}/`);
        return true;
    } catch (error) {
        console.error(`API Error deleting task ${taskId}:`, error.response?.data || error.message);
        throw error.response?.data || error;
    }
};