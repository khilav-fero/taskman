<template>
  <v-app>
    <v-main>
      <v-container v-if="authStore.getLoading && !initialCheckDone" fluid fill-height>
          <v-row align="center" justify="center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
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
const initialCheckDone = ref(false); // Track if checkAuth completed

onMounted(async () => {
  await authStore.checkAuth();
  initialCheckDone.value = true; // Allow rendering router-view
});
</script>

<style lang="scss">
html, body, #app { height: 100%; margin: 0; padding: 0; }
.fill-height { min-height: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
</style>