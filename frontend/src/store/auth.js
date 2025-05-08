import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import axios from 'axios';
import apiClient from '@/services/api';
import router from '@/router';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('authToken') || null);
  const user = ref(null);
  const isAuthenticated = ref(false); 
  const loading = ref(false);
  const error = ref(null);

  const getUser = computed(() => user.value);
  const getToken = computed(() => token.value);
  const getIsAuthenticated = computed(() => isAuthenticated.value);
  const getLoading = computed(() => loading.value);
  const getError = computed(() => error.value);
  const userRole = computed(() => user.value?.profile?.role || null); // CRITICAL FOR BUTTON

  function setAuthData(newToken, userData) {
    token.value = newToken;
    user.value = userData;
    isAuthenticated.value = true;
    localStorage.setItem('authToken', newToken);
    apiClient.defaults.headers.common['Authorization'] = `Token ${newToken}`;
    error.value = null;
  }

  function clearAuthData() {
    token.value = null;
    user.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem('authToken');
    delete apiClient.defaults.headers.common['Authorization'];
    error.value = null;
  }

  async function login(credentials) {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.post('/login/', credentials); 
      setAuthData(response.data.token, response.data.user);
      await router.push({ name: 'TaskList' }); // Or '/' which redirects
    } catch (err) {
      clearAuthData();
      if (axios.isAxiosError(err) && err.response) { error.value = err.response.data?.non_field_errors?.[0] || 'Login failed.'; }
      else { error.value = 'An unexpected error occurred.'; }
      console.error("Login error:", err);
    } finally { loading.value = false; }
  }

  async function register(userData) {
    loading.value = true;
    error.value = null;
    try {
      await apiClient.post('/register/', userData);
      await router.push({ name: 'Login' });
    } catch (err) {
       if (axios.isAxiosError(err) && err.response) {
         let errorMsg = 'Registration failed: ';
         const errors = err.response.data;
         if (typeof errors === 'object' && errors !== null) { errorMsg += Object.entries(errors).map(([field, messages]) => `${field}: ${messages.join(', ')}`).join('; '); }
         else { errorMsg += 'Please check your input.'; }
         error.value = errorMsg;
      } else { error.value = 'An unexpected error occurred.'; }
      console.error("Registration error:", err);
    } finally { loading.value = false; }
  }

  function logout() {
    clearAuthData();
    router.push({ name: 'Login' });
  }

  async function checkAuth() {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken && !isAuthenticated.value) { 
        loading.value = true; 
        token.value = storedToken;
        apiClient.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
        try {
            const response = await apiClient.get('/users/me/'); 
            setAuthData(storedToken, response.data);
        } catch (err) {
            console.error("Token verification failed:", err);
            clearAuthData(); 
        } finally {
            loading.value = false;
        }
    } else if (!storedToken) {
        clearAuthData(); // Clear if no token
    }
     
     if (!storedToken && !isAuthenticated.value) loading.value = false;
  }


  return {
    token, user, isAuthenticated, loading, error,
    getUser, getToken, getIsAuthenticated, getLoading, getError, userRole,
    login, register, logout, checkAuth,
  };
});