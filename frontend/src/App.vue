<template>
  <v-app>
    <!-- App Bar for Navigation/Logout -->
    <v-app-bar app color="primary" dark density="compact">
      <v-app-bar-title>Taskman</v-app-bar-title>
      <v-spacer></v-spacer>

      <!-- Show only if user is logged in -->
      <template v-if="authStore.getIsAuthenticated">
        <span class="mr-3 text-body-2">
          Welcome, {{ authStore.getUser?.username }} ({{ authStore.userRole }})
        </span>
        <v-btn icon @click="handleLogout">
          <v-icon>mdi-logout</v-icon>
          <v-tooltip activator="parent" location="bottom">Logout</v-tooltip>
        </v-btn>
      </template>
    </v-app-bar>

    <!-- Main Content Area -->
    <v-main>
      <v-container v-if="authStore.getLoading && !initialCheckDone" fluid fill-height>
          <v-row align="center" justify="center">
              <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          </v-row>
      </v-container>
      <!-- Router view renders the current page component -->
      <router-view v-else />
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const initialCheckDone = ref(false);

const handleLogout = () => {
  authStore.logout();
};

onMounted(async () => {
  // Check auth status only if not already authenticated (prevents redundant API call on hot reload)
  if (!authStore.getIsAuthenticated) {
      await authStore.checkAuth();
  }
  initialCheckDone.value = true;
});
</script>

<style lang="scss">
html, body, #app {
    height: 100%;
    margin: 0;
    padding: 0;
    /* Consider setting overflow if needed */
    /* overflow-y: auto; */
}
.fill-height {
    /* Ensure container takes full height for centering */
    min-height: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
/* Global styles can go here */
</style>