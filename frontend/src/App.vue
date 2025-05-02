<template>
  <v-app>
    <v-app-bar app color="primary" dark flat>
      <v-container fluid>
        <v-row align="center" justify="space-between" no-gutters>
          <!-- Left: App Title -->
          <v-col cols="auto" class="pl-4">
            <v-app-bar-title class="text-h6 font-weight-bold">Taskman</v-app-bar-title>
          </v-col>

          <!-- Right: User Info + Logout -->
          <v-col cols="auto" v-if="authStore.getIsAuthenticated">
            <div class="d-flex align-center">
              <v-avatar class="mr-2" size="32">
                <v-icon>mdi-account-circle</v-icon>
              </v-avatar>
              <div class="mr-4 text-caption white--text">
                {{ authStore.getUser?.username }} ({{ authStore.userRole }})
              </div>
              <v-btn icon @click="handleLogout" class="logout-btn" color="white">
                <v-icon>mdi-logout</v-icon>
                <v-tooltip activator="parent" location="bottom">Logout</v-tooltip>
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container v-if="authStore.getLoading && !initialCheckDone" class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-progress-circular indeterminate color="blue lighten-2" size="64"></v-progress-circular>
        </v-row>
      </v-container>
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
  background-color: #fafafa;
  font-family: 'Inter', sans-serif;
}

.fill-height {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn {
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.12) !important;
}

.v-btn {
  transition: background-color 0.3s ease;
}

.v-app-bar {
  background-color: #1e88e5; 
}

.v-btn.white {
  color: #1e88e5;
}

.white--text {
  color: #ffffff !important;
}

.main-bg {
  background-color: #f2f4f7;
  padding-top: 32px;
}
</style>
