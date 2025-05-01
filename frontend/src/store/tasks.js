// src/store/tasks.js
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { fetchTasks as apiFetchTasks } from '@/services/taskService'; // Ensure this service returns response data

export const useTasksStore = defineStore('tasks', () => {
  const tasksList = ref([]);
  const tasksLoading = ref(false);
  const tasksError = ref(null);

  // --- Getters (as computed refs) ---
  const getTasksList = computed(() => tasksList.value);
  const getTasksLoading = computed(() => tasksLoading.value);
  const getTasksError = computed(() => tasksError.value);

  // --- Actions ---
  async function fetchTasksAction() {
    tasksLoading.value = true;
    tasksError.value = null; // Clear previous error
    // Consider clearing the list here ONLY if you don't want to show stale data during loading
    // tasksList.value = [];
    try {
      // Assuming apiFetchTasks returns the actual data (e.g., response.data)
      const responseData = await apiFetchTasks();
      console.log('API Task Data Received in Store:', responseData);

      // Check if the response looks like a DRF paginated response
      if (responseData && typeof responseData === 'object' && Array.isArray(responseData.results)) {
          tasksList.value = responseData.results;
          console.log('Processed paginated results:', tasksList.value);
          // You could potentially store pagination info here too if needed
          // e.g., const paginationInfo = ref({ count: responseData.count, next: responseData.next, previous: responseData.previous });
      }
      // Check if it's just a plain array
      else if (Array.isArray(responseData)) {
          console.warn("Received task data was an array. Handling array directly.");
          tasksList.value = responseData;
      }
      // Handle other unexpected formats
      else {
          console.error("Received task data is not in a known format:", responseData);
          tasksList.value = []; // Ensure list is empty on format error
          tasksError.value = 'Received unexpected data format for tasks.';
      }
    } catch (err) {
      console.error("Error fetching tasks in store:", err.response?.data || err.message);
      const detail = err.response?.data?.detail; // Try to get DRF detail message
      tasksError.value = detail || err.message || 'Failed to load tasks. Please try again.';
      tasksList.value = []; // Ensure list is empty on error
    } finally {
      tasksLoading.value = false;
    }
  }

  // Action to clear the error state, callable from components
  function clearTasksError() {
    tasksError.value = null;
  }

  // --- Return Store API ---
  return {
    // State (refs are automatically unwrapped by Pinia outside setup)
    tasksList,
    tasksLoading,
    tasksError,

    // Getters (computed refs)
    getTasksList,
    getTasksLoading,
    getTasksError,

    // Actions
    fetchTasksAction,
    clearTasksError, // <-- Expose the new action
  };
});