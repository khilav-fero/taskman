// src/services/taskService.js
import apiClient from './api'; // Import the configured Axios instance

/**
 * Fetches the list of tasks from the backend.
 * Assumes authentication token is handled by apiClient interceptor.
 * @returns {Promise<Array>} A promise that resolves with the array of task objects.
 */
export const fetchTasks = async () => {
  try {
    const response = await apiClient.get('/tasks/');
    // The actual list is often inside response.data.results if using pagination
    return response.data.results || response.data;
  } catch (error) {
    console.error("API Error fetching tasks:", error);
    // Re-throw error to be handled by the store action
    throw error;
  }
};

// Add functions for createTask, updateTask, deleteTask, fetchTaskDetail, fetchTaskHistory etc. later