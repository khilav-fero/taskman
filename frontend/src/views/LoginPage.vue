<template>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6" lg="4">
          <v-card class="login-card elevation-6">
            <v-progress-linear
              :active="authStore.getLoading"
              indeterminate
              color="#4A90E2"
              absolute
              top
            />
  
            <v-toolbar color="#4A90E2" dark flat class="rounded-t">
              <v-toolbar-title>Welcome Back</v-toolbar-title>
            </v-toolbar>
  
            <v-card-text class="pt-4 px-5">
              <v-form @submit.prevent="handleLogin">
                <v-alert
                  v-if="authStore.getError"
                  type="error"
                  variant="tonal"
                  closable
                  density="compact"
                  class="mb-4"
                  @update:modelValue="clearError"
                  title="Login Error"
                >
                  {{ authStore.getError }}
                </v-alert>
  
                <v-text-field
                  v-model="formData.username"
                  label="Username"
                  name="username"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  class="mb-3"
                  required
                  color="#4A90E2"
                  :error-messages="v$.username.$errors.map(e => e.$message)"
                  @blur="v$.username.$touch()"
                />
  
                <v-text-field
                  v-model="formData.password"
                  label="Password"
                  name="password"
                  prepend-inner-icon="mdi-lock"
                  variant="outlined"
                  type="password"
                  class="mb-3"
                  required
                  color="#4A90E2"
                  :error-messages="v$.password.$errors.map(e => e.$message)"
                  @blur="v$.password.$touch()"
                />
  
                <v-card-actions class="pa-0 mt-4 d-flex justify-space-between align-center">
                  <router-link :to="{ name: 'Register' }" class="text-caption text-grey-darken-1">
                    Need an account?
                  </router-link>
  
                  <v-btn
                    type="submit"
                    :loading="authStore.getLoading"
                    :disabled="v$.$invalid || authStore.getLoading"
                    size="large"
                    variant="flat"
                    color="#4A90E2"
                    class="text-white font-weight-bold"
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
  
  <style scoped>
  .fill-height {
    min-height: 90vh;
    background-color: #f5f7fa;
  }
  
  .login-card {
    background-color: #ffffff;
    border-radius: 12px;
  }
  
  .v-text-field {
    border-radius: 8px;
  }
  
  .v-toolbar-title {
    font-size: 1.25rem;
    font-weight: 500;
  }
  
  .v-btn {
    border-radius: 8px;
    text-transform: none;
  }
  </style>
  