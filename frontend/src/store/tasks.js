import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import {
    fetchTasks as apiFetchTasks,
    createTask as apiCreateTask,
    updateTask as apiUpdateTask
} from '@/services/taskService';

export const useTasksStore = defineStore('tasks', () => {
  const tasksList = ref([]);
  const tasksLoading = ref(false);
  const tasksError = ref(null);
  const formLoading = ref(false);
  const formError = ref(null);

  const getTasksList = computed(() => tasksList.value);
  const getTasksLoading = computed(() => tasksLoading.value);
  const getTasksError = computed(() => tasksError.value);
  const getFormLoading = computed(() => formLoading.value);
  const getFormError = computed(() => formError.value);

  function clearFormError() {
      formError.value = null;
  }
  function clearTasksError() {
      tasksError.value = null;
  }

  async function fetchTasksAction() {
    tasksLoading.value = true;
    tasksError.value = null;
    try {
      const responseData = await apiFetchTasks();
      if (responseData && typeof responseData === 'object' && Array.isArray(responseData.results)) {
          tasksList.value = responseData.results;
      } else {
          console.warn("Received task data not paginated:", responseData);
          tasksList.value = Array.isArray(responseData) ? responseData : [];
      }
      return tasksList.value;
    } catch (err) {
      console.error("Error fetching tasks in store:", err);
      tasksError.value = err.response?.data?.detail || 'Failed to load tasks.';
      tasksList.value = [];
      throw err;
    } finally {
      tasksLoading.value = false;
    }
  }

  async function createTaskAction(taskData) {
      formLoading.value = true;
      formError.value = null;
      try {
          const newTask = await apiCreateTask(taskData);
          await fetchTasksAction();
          return newTask;
      } catch (err) {
          console.error("Error creating task in store:", err);
          formError.value = err.response?.data || 'Failed to create task.';
          throw err;
      } finally {
          formLoading.value = false;
      }
  }

  async function updateTaskAction(taskId, taskData) {
      formLoading.value = true;
      formError.value = null;
      try {
          const updatedTask = await apiUpdateTask(taskId, taskData);
          await fetchTasksAction();
          return updatedTask;
      } catch (err) {
          console.error("Error updating task in store:", err);
          formError.value = err.response?.data || 'Failed to update task.';
          throw err;
      } finally {
          formLoading.value = false;
      }
  }

  return {
    tasksList,
    tasksLoading,
    tasksError,
    formLoading,
    formError,
    getTasksList,
    getTasksLoading,
    getTasksError,
    getFormLoading,
    getFormError,
    fetchTasksAction,
    createTaskAction,
    updateTaskAction,
    clearFormError,
    clearTasksError, 
  };
});