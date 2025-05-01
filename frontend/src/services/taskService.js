import apiClient from './api'; 

/**
 * @returns {Promise<Array>} A promise that resolves with the array of task objects.
 */
export const fetchTasks = async () => {
  try {
    const response = await apiClient.get('/tasks/');
    return response.data.results || response.data;
  } catch (error) {
    console.error("API Error fetching tasks:", error);
    throw error;
  }
};

