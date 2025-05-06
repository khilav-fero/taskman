import apiClient from './api'; // Corrected import to match previous use

export async function fetchAllUsers() {
  try {
    const response = await apiClient.get('/users/');
    return response.data.results || response.data || [];
  } catch (error) {
    console.error("API Error fetching users:", error.response?.data || error.message);
    throw error;
  }
}

export async function createUserApi(userData) {
    try {
        const response = await apiClient.post('/users/', userData);
        return response.data;h
    } catch (error) {
        console.error("API Error creating user:", error.response?.data || error);
        throw error;
    }
}

export async function updateUserApi(userId, userData) {
    try {
        const response = await apiClient.patch(`/users/${userId}/`, userData);
        return response.data;
    } catch (error) {
        console.error(`API Error updating user ${userId}:`, error.response?.data || error);
        throw error;
    }
}

export const updateUserRole = async (userId, newRole) => {
    try {
        const response = await apiClient.patch(`/users/${userId}/update-role/`, { role: newRole });
        return response.data;
    } catch (error) {
        console.error(`API Error updating role for user ${userId}:`, error.response?.data || error);
        throw error;
    }
};

export const deleteUserApi = async (userId) => {
    try {
        await apiClient.delete(`/users/${userId}/`);
    } catch (error) {
        console.error(`API Error deleting user ${userId}:`, error.response?.data || error);
        throw error;
    }
};