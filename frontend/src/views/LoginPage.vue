<template>
  <v-container class="fill-height themed-background" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="login-card" elevation="12" :color="$vuetify.theme.current.colors.surface">
          <v-progress-linear
            :active="authStore.getLoading"
            indeterminate
            color="primary"
            absolute
            top
          />

          <v-toolbar color="primary" dark flat class="rounded-t-lg">
            <v-toolbar-title class="text-h6 font-weight-medium">Welcome Back</v-toolbar-title>
          </v-toolbar>

          <v-card-text class="pa-6">
            <v-form @submit.prevent="handleLogin">
              <v-alert
                v-if="authStore.getError"
                type="error"
                variant="tonal"
                closable
                density="compact"
                class="mb-5"
                @update:modelValue="clearError"
                title="Login Error"
              >
                {{ authStore.getError }}
              </v-alert>

              <v-text-field
                v-model="formData.username"
                label="Username"
                name="username"
                prepend-inner-icon="mdi-account-outline"
                variant="outlined"
                class="mb-4"
                required
                color="primary"
                :error-messages="v$.username.$errors.map(e => e.$message)"
                @blur="v$.username.$touch()"
                density="comfortable"
              />

              <v-text-field
                v-model="formData.password"
                label="Password"
                name="password"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
                type="password"
                class="mb-4"
                required
                color="primary"
                :error-messages="v$.password.$errors.map(e => e.$message)"
                @blur="v$.password.$touch()"
                density="comfortable"
              />

              <v-card-actions class="pa-0 mt-5 d-flex justify-space-between align-center">
                <router-link :to="{ name: 'Register' }" class="text-caption registration-link">
                  Need an account? Register
                </router-link>

                <v-btn
                  type="submit"
                  :loading="authStore.getLoading"
                  :disabled="v$.$invalid || authStore.getLoading"
                  size="large"
                  variant="flat"
                  color="primary"
                  class="login-button font-weight-bold"
                >
                  Login
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { reactive, computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useVuelidate } from '@vuelidate/core';
import { required, helpers } from '@vuelidate/validators';

const authStore = useAuthStore();

const formData = reactive({
  username: '',
  password: '',
});

const rules = computed(() => ({
  username: { required: helpers.withMessage('Username is required', required) },
  password: { required: helpers.withMessage('Password is required', required) },
}));

const v$ = useVuelidate(rules, formData);

const handleLogin = async () => {
  const isValid = await v$.value.$validate();
  if (!isValid) return;

  await authStore.login({
    username: formData.username,
    password: formData.password
  });
};

const clearError = () => {
  authStore.error = null;
};
</script>

<style lang="scss" scoped>
.fill-height {
  min-height: 100vh; // Ensure it covers the viewport if content is short
}

.themed-background {
  // Vuetify 3 applies theme background to v-app, so this can often be removed
  // or set to transparent if v-app handles it.
  // If you see issues, explicitly set:
  // background-color: rgb(var(--v-theme-background));
}

.login-card {
  border-radius: 12px;
  // The surface color is applied via :color prop directly on v-card
  // color: rgb(var(--v-theme-on-surface)); // for text on the card, if not inherited well
}

.v-toolbar-title {
  color: rgb(var(--v-theme-on-primary));
}

.registration-link {
  color: rgba(var(--v-theme-on-surface-rgb), 0.7);
  text-decoration: none;
  transition: color 0.2s ease-in-out;

  &:hover {
    color: rgb(var(--v-theme-primary));
    text-decoration: underline;
  }
}

.login-button {
  color: rgb(var(--v-theme-on-primary)); // Ensure text color contrasts with primary button
  min-width: 120px; // Give the button a bit more presence
}

// General adjustments for text fields in dark theme if needed
// For example, if placeholder text is hard to see:
// :deep(.v-field__input::placeholder) {
//   color: rgba(var(--v-theme-on-surface-rgb), 0.6) !important;
//   opacity: 1;
// }
</style>