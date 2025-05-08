import apiClient from './api';

export async function fetchAllUsers(queryParams = null) {
  try {
    let url = '/users/';
    if (queryParams && queryParams.toString()) {
      url += `?${queryParams.toString()}`;
    }
    const response = await apiClient.get(url);
    return {
      results: response.data.results || response.data || [],
      count: response.data.count || 0,
      next: response.data.next || null,
      previous: response.data.previous || null,
    };
  } catch (error) {
    console.error("API Error fetching users:", error.response?.data || error.message);
    throw error.response?.data || error;
  }
}

export async function fetchUserById(userId) {
  try {
    const response = await apiClient.get(`/users/${userId}/`);
    return response.data;
  } catch (error) {
    console.error(`API Error fetching user ${userId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
}

export async function createUserApi(userData) {
    try {
        const response = await apiClient.post('/users/', userData);
        return response.data;
    } catch (error) {
        console.error("API Error creating user:", error.response?.data || error);
        throw error.response?.data || error;
    }
}

export async function updateUserApi(userId, userData) {
    try {
        const payload = { ...userData };
        if (payload.first_name === '') delete payload.first_name;
        if (payload.last_name === '') delete payload.last_name;

        const response = await apiClient.patch(`/users/${userId}/`, payload);
        return response.data;
    } catch (error) {
        console.error(`API Error updating user ${userId}:`, error.response?.data || error);
        throw error.response?.data || error;
    }
}

export const updateUserRole = async (userId, newRole) => {
    try {
        const response = await apiClient.patch(`/users/${userId}/update-role/`, { role: newRole });
        return response.data;
    } catch (error) {
        console.error(`API Error updating role for user ${userId}:`, error.response?.data || error);
        throw error.response?.data || error;
    }
};

export const deleteUserApi = async (userId) => {
    try {
        await apiClient.delete(`/users/${userId}/`);
    } catch (error) {
        console.error(`API Error deleting user ${userId}:`, error.response?.data || error);
        throw error.response?.data || error;
    }
};