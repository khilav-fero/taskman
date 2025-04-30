import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
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
  const userRole = computed(() => user.value?.profile?.role || null); 

  function setAuthData(newToken, userData) {
      token.value = newToken;
      user.value = userData;
      isAuthenticated.value = true;
      localStorage.setItem('authToken', newToken); // Persist token
      apiClient.defaults.headers.common['Authorization'] = `Token ${newToken}`;
      error.value = null; // Clear previous errors
  }

  function clearAuthData() {
      token.value = null;
      user.value = null;
      isAuthenticated.value = false;
      localStorage.removeItem('authToken'); // Remove token
      delete apiClient.defaults.headers.common['Authorization'];
      error.value = null;
  }

  async function login(credentials) {
      loading.value = true;
      error.value = null;
      try {
          const response = await apiClient.post('/login/', credentials);
          setAuthData(response.data.token, response.data.user);
          await router.push({ name: 'TaskList' });
      } catch (err) {
          clearAuthData(); // Clear state on error
          error.value = err.response?.data?.non_field_errors?.[0] || 'Login failed. Invalid credentials.';
          console.error("Login error:", err.response?.data || err.message);
      } finally {
          loading.value = false; // Always stop loading
      }
  }

  async function register(userData) {
    loading.value = true;
    error.value = null;
    try {
        await apiClient.post('/register/', userData);
        await router.push({ name: 'Login' });
    } catch (err) {
        let errorMsg = 'Registration failed: ';
        if (err.response && typeof err.response.data === 'object') {
             errorMsg += Object.entries(err.response.data)
                .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
                .join('; ');
        } else {
            errorMsg += 'Please check your input or try again later.';
        }
        error.value = errorMsg;
        console.error("Registration error:", err.response?.data || err.message);
    } finally {
      loading.value = false;
    }
  }

  function logout() {
      clearAuthData();
      router.push({ name: 'Login' });
  }

  async function checkAuth() {

    const storedToken = localStorage.getItem('authToken');
    if (storedToken && !isAuthenticated.value) { 
        console.log('checkAuth: Found token, attempting verification...');
        loading.value = true;
        token.value = storedToken;
        apiClient.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
        try {
  
            const response = await apiClient.get('/users/me/');
            setAuthData(storedToken, response.data); 
            console.log('checkAuth: Token verified.');
        } catch (err) {
            console.error("checkAuth: Token verification failed, logging out.", err.response?.data || err.message);
            clearAuthData(); 
        } finally {
            loading.value = false;
        }
    } else if (!storedToken) {
        clearAuthData();
    }
  }

  return {
      token,
      user,
      isAuthenticated,
      loading,
      error,
      getUser,
      getToken,
      getIsAuthenticated,
      getLoading,
      getError,
      userRole,
      login,
      register,
      logout,
      checkAuth,
  };
});