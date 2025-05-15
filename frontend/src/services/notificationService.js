import apiClient from './api';

export const fetchNotifications = async (params = {}) => {
  try {
    const response = await apiClient.get('/notifications/', { params: params });
    return response.data;
  } catch (error) {
    console.error("API Error fetching notifications:", error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const fetchUnreadNotificationCount = async () => {
  try {
    const response = await apiClient.get('/notifications/unread_count/');
    return response.data;
  } catch (error) {
    console.error("API Error fetching unread notification count:", error.response?.data || error.message);
    throw error.response?.data || error;
  }
};