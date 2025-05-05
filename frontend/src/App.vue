<template>
  <v-app>
    <v-app-bar app color="primary" dark flat density="compact">
      <v-container fluid>
        <v-row align="center" no-gutters>
          <v-col cols="auto">
            <v-app-bar-title class="text-h6 font-weight-medium">
              Taskman
            </v-app-bar-title>
          </v-col>

          <v-col class="d-flex justify-start pl-6">
            <template v-if="authStore.getIsAuthenticated">
              <v-btn
                :to="{ name: 'TaskList' }" text class="mx-1"
                variant="text" prepend-icon="mdi-view-list"
              >
                  Tasks
              </v-btn>
              <!-- CONDITIONAL USERS BUTTON -->
              <v-btn
                  v-if="isAdminOrManager"
                  :to="{ name: 'UserList' }"
                  text class="mx-1" variant="text" prepend-icon="mdi-account-group"
              >
                  Users
              </v-btn>
            </template>
          </v-col>

          <v-col cols="auto" class="d-flex justify-end align-center">
            <template v-if="authStore.getIsAuthenticated">
               <v-chip label size="small" class="mr-1" variant="elevated" color="primary-darken-1">
                 <v-icon start icon="mdi-account-circle"></v-icon>
                 {{ authStore.getUser?.username }} ({{ authStore.userRole }})
              </v-chip>
              <v-tooltip location="bottom">
                 <template v-slot:activator="{ props }">
                     <v-btn v-bind="props" icon="mdi-logout" @click="handleLogout" variant="text"></v-btn>
                 </template>
                <span>Logout</span>
              </v-tooltip>
            </template>
            <template v-else>
               <v-btn :to="{ name: 'Login' }" text variant="text">Login</v-btn>
               <v-btn :to="{ name: 'Register' }" text variant="text">Register</v-btn>
            </template>
          </v-col>
        </v-row>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container v-if="authStore.getLoading && !initialCheckDone" class="fill-height" fluid>
          <v-row align="center" justify="center">
              <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          </v-row>
      </v-container>
      <router-view v-else />
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const initialCheckDone = ref(false);

const isAdminOrManager = computed(() => {
    const role = authStore.userRole;
    return role === 'ADMIN' || role === 'MANAGER';
});

const handleLogout = () => { authStore.logout(); };

onMounted(async () => {
  if (!authStore.getIsAuthenticated) { await authStore.checkAuth(); }
  initialCheckDone.value = true;
});
</script>

<style lang="scss">
html, body, #app { height: 100%; margin: 0; padding: 0; font-family: 'Roboto', sans-serif; }
.fill-height { min-height: 100%; display: flex; align-items: center; justify-content: center;}
.v-app-bar .v-btn { text-transform: none; }
</style>