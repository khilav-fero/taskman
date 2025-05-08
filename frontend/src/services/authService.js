import apiClient from './api';

export async function loginUserApi(credentials) {
  try {
    const response = await apiClient.post('/login/', credentials);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
}

export async function registerUserApi(userData) {
  try {
    const response = await apiClient.post('/register/', userData);
    return response.data;
  } catch (error) {
    let errorMessages = [];
    const errorData = error.response?.data;

    if (errorData && typeof errorData === 'object') {
        for (const key in errorData) {
            if (Array.isArray(errorData[key])) {
                errorMessages.push(`${key}: ${errorData[key].join(', ')}`);
            } else {
                errorMessages.push(`${key}: ${errorData[key]}`);
            }
        }
    }
    if (!errorMessages.length) {
        errorMessages.push(errorData?.detail || 'An unexpected error occurred during registration.');
    }
    throw new Error(errorMessages.join('; '));
  }
}

export async function getCurrentUserApi() {
  try {
    const response = await apiClient.get('/users/me/');
    return response.data;
  } catch (error) {
    if (error.response?.status !== 401) {
        throw error;
    }
    return null;
  }
}