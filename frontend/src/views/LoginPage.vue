<template>
  <v-container class="fill-height themed-background" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="login-card" elevation="12" :color="$vuetify.theme.current.colors.surface">
          <v-progress-linear
            :active="loading"
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
                v-if="errorMessage"
                type="error"
                variant="tonal"
                closable
                density="compact"
                class="mb-5"
                @update:modelValue="clearError"
                title="Login Error"
              >
                {{ errorMessage }}
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
                  :loading="loading"
                  :disabled="v$.$invalid || loading"
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
import { reactive, computed, ref } from 'vue';
import { useVuelidate } from '@vuelidate/core';
import { required, helpers } from '@vuelidate/validators';
import { loginUserApi } from '@/services/authService';

const emit = defineEmits(['login-success', 'login-failure']);

const formData = reactive({
  username: '',
  password: '',
});

const loading = ref(false);
const errorMessage = ref(null);

const rules = computed(() => ({
  username: { required: helpers.withMessage('Username is required', required) },
  password: { required: helpers.withMessage('Password is required', required) },
}));

const v$ = useVuelidate(rules, formData);

const handleLogin = async () => {
  const isValid = await v$.value.$validate();
  if (!isValid) return;

  loading.value = true;
  errorMessage.value = null;

  try {
    const responseData = await loginUserApi({
      username: formData.username,
      password: formData.password
    });
    emit('login-success', responseData);
  } catch (error) {
    const apiError = error;
    if (apiError && apiError.non_field_errors && Array.isArray(apiError.non_field_errors)) {
        errorMessage.value = apiError.non_field_errors.join(' ');
    } else if (apiError && apiError.detail) {
        errorMessage.value = apiError.detail;
    } else if (typeof apiError === 'string') {
        errorMessage.value = apiError;
    } else if (apiError && typeof apiError === 'object' && Object.keys(apiError).length > 0) {
        errorMessage.value = Object.entries(apiError).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`).join('; ');
    }
    else {
        errorMessage.value = 'Login failed. Please check your credentials or try again later.';
    }
    emit('login-failure', errorMessage.value);
  } finally {
    loading.value = false;
  }
};

const clearError = () => {
  errorMessage.value = null;
};
</script>

<style lang="scss" scoped>
.fill-height {
  min-height: 100vh;
}
.themed-background {
}
.login-card {
  border-radius: 12px;
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
  color: rgb(var(--v-theme-on-primary));
  min-width: 120px;
}
</style>