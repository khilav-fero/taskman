import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { fetchTasks as apiFetchTasks } from '@/services/taskService';

export const useTasksStore = defineStore('tasks', () => {
  const tasksList = ref([]);
  const tasksLoading = ref(false);
  const tasksError = ref(null);

  const getTasksList = computed(() => tasksList.value);
  const getTasksLoading = computed(() => tasksLoading.value);
  const getTasksError = computed(() => tasksError.value);

  async function fetchTasksAction() {
    tasksLoading.value = true;
    tasksError.value = null;
    try {
      const responseData = await apiFetchTasks();
      console.log('API Task Data Received in Store:', responseData);

      if (responseData && typeof responseData === 'object' && Array.isArray(responseData.results)) {
          tasksList.value = responseData.results;
          console.log('Processed paginated results:', tasksList.value);
      }
      else if (Array.isArray(responseData)) {
          console.warn("Received task data was an array. Handling array directly.");
          tasksList.value = responseData;
      }
      else {
          console.error("Received task data is not in a known format:", responseData);
          tasksList.value = [];
          tasksError.value = 'Received unexpected data format for tasks.';
      }
    } catch (err) {
      console.error("Error fetching tasks in store:", err.response?.data || err.message);
      const detail = err.response?.data?.detail;
      tasksError.value = detail || err.message || 'Failed to load tasks. Please try again.';
      tasksList.value = [];
    } finally {
      tasksLoading.value = false;
    }
  }

  function clearTasksError() {
    tasksError.value = null;
  }

  return {
    tasksList,
    tasksLoading,
    tasksError,
    getTasksList,
    getTasksLoading,
    getTasksError,
    fetchTasksAction,
    clearTasksError,
  };
});
