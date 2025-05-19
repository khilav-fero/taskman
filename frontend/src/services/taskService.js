import apiClient from './api'; // Assuming you have an apiClient configured

export const fetchTasks = async (params = {}) => {
  try {
    const response = await apiClient.get('/tasks/', { params: params });
    return response.data;
  } catch (error) {
    console.error("API Error fetching tasks:", error.response?.data || error.message);
    throw error.response?.data || error; // Re-throw for component to handle
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

export const deleteTaskApi = async (taskId) => {
    try {
        await apiClient.delete(`/tasks/${taskId}/`);
        return true; // Indicate success
    } catch (error) {
        console.error(`API Error deleting task ${taskId}:`, error.response?.data || error.message);
        throw error.response?.data || error;
    }
};

// --- Task History ---
export const fetchTaskHistory = async (taskId) => {
  try {
    const response = await apiClient.get(`/tasks/${taskId}/history/`);
    // Ensure it returns an array, or an object with a 'results' array
    return response.data;
  } catch (error) {
    console.error(`API Error fetching history for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

// --- Task Comments ---
export const fetchTaskComments = async (taskId, params = {}) => {
  try {
    const response = await apiClient.get(`/tasks/${taskId}/comments/`, { params: params });
    // Ensure it returns an array, or an object with a 'results' array
    return response.data;
  } catch (error) {
    console.error(`API Error fetching comments for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const addTaskComment = async (taskId, commentData) => {
  try {
    // commentData should be like { text: "My comment" }
    const response = await apiClient.post(`/tasks/${taskId}/comments/`, commentData);
    return response.data; // Backend should return the created comment object
  } catch (error) {
    console.error(`API Error adding comment for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const deleteTaskComment = async (taskId, commentId) => {
  try {
    // Note: The URL structure might vary. Some APIs use /comments/{commentId}/
    // Yours seems to be /tasks/{taskId}/comments/{commentId}/ which is also common.
    await apiClient.delete(`/tasks/${taskId}/comments/${commentId}/`);
    return true; // Indicate success
  } catch (error) {
    console.error(`API Error deleting comment ${commentId} for task ${taskId}:`, error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

// (If you add comment editing later)
// export const updateTaskComment = async (taskId, commentId, commentData) => {
//   try {
//     const response = await apiClient.patch(`/tasks/${taskId}/comments/${commentId}/`, commentData);
//     return response.data;
//   } catch (error) {
//     console.error(`API Error updating comment ${commentId} for task ${taskId}:`, error.response?.data || error.message);
//     throw error.response?.data || error;
//   }
// };