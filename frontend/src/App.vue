<template>
  <v-app id="taskman-app">
    <v-main>
      <v-container v-if="appLoading" class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-progress-circular indeterminate color="primary" size="50" width="3"></v-progress-circular>
        </v-row>
      </v-container>
      <router-view v-else v-slot="{ Component, route: currentRoute }">
        <component
          :is="Component"
          :key="currentRoute.path"
          @login-success="handleLoginSuccess"
          @registration-success="handleRegistrationSuccess"
          @logout-request="handleLogout"
        />
      </router-view>
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted, onUnmounted, ref, provide } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getCurrentUserApi } from '@/services/authService';

const route = useRoute();
const router = useRouter();

const currentUser = ref(null);
const isAuthenticated = ref(false);
const appLoading = ref(true);

provide('currentUser', currentUser);
provide('isAuthenticated', isAuthenticated);

async function checkAuthOnLoad() {
  appLoading.value = true;
  const token = localStorage.getItem('authToken');
  if (token) {
    try {
      const user = await getCurrentUserApi();
      if (user) {
        currentUser.value = user;
        isAuthenticated.value = true;
        localStorage.setItem('authUser', JSON.stringify(user));
      } else {
        await performLogoutActions();
      }
    } catch (error) {
      console.warn('Auth check failed:', error);
      await performLogoutActions();
    }
  } else {
    currentUser.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem('authUser');
  }
  appLoading.value = false;
}

function handleLoginSuccess(authData) {
  localStorage.setItem('authToken', authData.token);
  localStorage.setItem('authUser', JSON.stringify(authData.user));
  currentUser.value = authData.user;
  isAuthenticated.value = true;
  appLoading.value = false;

  const redirectPath = route.query.redirect || { name: 'TaskList' };
  router.push(redirectPath);
}

function handleRegistrationSuccess() {
    router.push({ name: 'Login', query: { registered: 'true' } });
}

async function performLogoutActions() {
  localStorage.removeItem('authToken');
  localStorage.removeItem('authUser');
  currentUser.value = null;
  isAuthenticated.value = false;
}

async function handleLogout() {
  await performLogoutActions();
  router.push({ name: 'Login' });
}

function handleAuthExpiredEvent() {
  if (isAuthenticated.value) {
    console.log('Auth expired event received, logging out.');
    handleLogout();
  }
}

onMounted(async () => {
  await checkAuthOnLoad();
  window.addEventListener('auth-expired', handleAuthExpiredEvent);
});

onUnmounted(() => {
  window.removeEventListener('auth-expired', handleAuthExpiredEvent);
});
</script>

<style lang="scss">
</style>