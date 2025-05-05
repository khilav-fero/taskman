import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { fetchAllUsers as apiFetchUsers } from '@/services/userService';

export const useUsersStore = defineStore('users', () => {

  const userList = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  const getUserList = computed(() => userList.value);
  const getUsersLoading = computed(() => isLoading.value);
  const getUsersError = computed(() => error.value);

  async function fetchUsersAction() {
    isLoading.value = true;
    error.value = null;
    try {
      const fetchedUsers = await apiFetchUsers();
      userList.value = fetchedUsers;
    } catch (fetchError) {
      console.error("User Store: Error fetching users", fetchError);
      error.value = 'Could not load user list.';
      userList.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  function clearUsersError() {
      error.value = null;
  }

  return {
    userList,
    isLoading,
    error,
    getUserList,
    getUsersLoading,
    getUsersError,
    fetchUsersAction,
    clearUsersError,
  };
});