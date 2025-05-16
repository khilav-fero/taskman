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

export const markNotificationAsRead = async (notificationId) => {
  try {
    const response = await apiClient.post(`/notifications/${notificationId}/mark_as_read/`);
    return response.data;
  } catch (error) {
    console.error(`API Error marking notification ${notificationId} as read:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const markAllNotificationsAsRead = async () => {
  try {
    const response = await apiClient.post('/notifications/mark_all_as_read/');
    return response.data;
  } catch (error) {
    console.error("API Error marking all notifications as read:", error.response?.data || error.message);
    throw error.response?.data || error;
  }
};