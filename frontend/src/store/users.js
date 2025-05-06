import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import {
    fetchAllUsers as apiFetchUsers,
    createUserApi as apiCreateUser,
    updateUserApi as apiUpdateUser,
    updateUserRole as apiUpdateUserRole,
    deleteUserApi as apiDeleteUser
} from '@/services/userService';

export const useUsersStore = defineStore('users', () => {

  const userList = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const formLoading = ref(false);
  const formError = ref(null);

  const getUserList = computed(() => userList.value);
  const getUsersLoading = computed(() => isLoading.value);
  const getUsersError = computed(() => error.value);
  const getFormLoading = computed(() => formLoading.value);
  const getFormError = computed(() => formError.value);

  function clearUsersError() { error.value = null; }
  function clearFormError() { formError.value = null; }

  async function fetchUsersAction() {
    isLoading.value = true;
    error.value = null;
    try {
      const fetchedUsers = await apiFetchUsers();
      userList.value = fetchedUsers;
    } catch (fetchError) {
      error.value = fetchError.response?.data?.detail || 'Could not load user list.';
      userList.value = [];
      console.error("User Store: Error fetching users", fetchError);
    } finally {
      isLoading.value = false;
    }
  }

  async function createUserAction(userData) {
    formLoading.value = true;
    formError.value = null;
    try {
      await apiCreateUser(userData);
      return true;
    } catch (err) {
      formError.value = err.response?.data?.detail || err.response?.data || 'Failed to create user.';
      console.error("User Store: Error creating user", err);
      return false;
    } finally {
      formLoading.value = false;
    }
  }

  async function updateUserAction(userId, userData) {
    formLoading.value = true;
    formError.value = null;
    try {
      await apiUpdateUser(userId, userData);
      return true;
    } catch (err) {
      formError.value = err.response?.data?.detail || err.response?.data || 'Failed to update user.';
      console.error("User Store: Error updating user", err);
      return false;
    } finally {
      formLoading.value = false;
    }
  }

  async function updateUserRoleAction(userId, newRole) {
      formLoading.value = true;
      formError.value = null;
      try {
          const updatedProfileData = await apiUpdateUserRole(userId, newRole);
          const index = userList.value.findIndex(u => u.id === userId);
          if (index !== -1) {
              if (userList.value[index].profile) {
                  userList.value[index].profile.role = updatedProfileData.role;
              } else {
                 userList.value[index].profile = { role: updatedProfileData.role };
              }
          }
          return true;
      } catch (err) {
          formError.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to update role.';
          console.error("User Store: Error updating role", err);
          return false;
      } finally {
          formLoading.value = false;
      }
  }

  async function deleteUserAction(userId) {
      formLoading.value = true;
      formError.value = null;
      try {
          await apiDeleteUser(userId);
          userList.value = userList.value.filter(u => u.id !== userId);
          return true;
      } catch (err) {
          formError.value = err.response?.data?.detail || 'Failed to delete user.';
           console.error("User Store: Error deleting user", err);
          return false;
      } finally {
          formLoading.value = false;
      }
  }

  return {
    userList, isLoading, error, formLoading, formError,
    getUserList, getUsersLoading, getUsersError, getFormLoading, getFormError,
    fetchUsersAction, clearUsersError, clearFormError,
    createUserAction,
    updateUserAction,
    updateUserRoleAction,
    deleteUserAction,
  };
});