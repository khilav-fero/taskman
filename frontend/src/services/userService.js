import apiClient from './api';

/**
 * Fetches the list of users for assignment dropdowns.
 * Assumes backend returns a list (paginated or not).
 * @returns {Promise<Array<{id: number, username: string}>>}
 */
export const fetchAllUsers = async () => {
  try {
    const response = await apiClient.get('/users/'); // Target the correct user list endpoint
    return response.data.results || response.data || [];
  } catch (error) {
    console.error("API Error fetching users:", error.response?.data || error.message);
    return []; // Return empty array on failure
  }
};