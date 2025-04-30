<template>
    <v-container class="fill-height" fluid>
      <v-row align-items="center" justify="center">
        <v-col cols="12" sm="8" md="6" lg="4">
          <v-card class="elevation-12">
            <v-progress-linear
              :active="authStore.getLoading"
              indeterminate
              color="primary"
              absolute
              top
            ></v-progress-linear>
  
            <v-toolbar color="primary" dark flat>
              <v-toolbar-title>Login</v-toolbar-title>
            </v-toolbar>
  
            <v-card-text class="pt-4">
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
                  class="mb-2"
                  required
                  :error-messages="v$.username.$errors.map(e => e.$message)"
                  @blur="v$.username.$touch()"
                ></v-text-field>
  
                <v-text-field
                  v-model="formData.password"
                  label="Password"
                  name="password"
                  prepend-inner-icon="mdi-lock"
                  variant="outlined"
                  type="password"
                  class="mb-2"
                  required
                  :error-messages="v$.password.$errors.map(e => e.$message)"
                  @blur="v$.password.$touch()"
                ></v-text-field>
  
                <v-card-actions class="pa-0 mt-2">
                   <router-link :to="{ name: 'Register' }" class="text-body-2 ml-1">
                     Need an account?
                   </router-link>
                   <v-spacer></v-spacer>
                   <v-btn
                     type="submit"
                     color="primary"
                     :loading="authStore.getLoading"
                     :disabled="v$.$invalid || authStore.getLoading"
                     size="large"
                     variant="elevated"
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
  }
  </script>
  
  <style scoped>
  .fill-height {
    min-height: 90vh;
  }
  </style>