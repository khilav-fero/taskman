<template>
  <v-container class="fill-height themed-background" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="5" xl="4">
        <v-card class="register-card" elevation="12" :color="$vuetify.theme.current.colors.surface">
          <v-progress-linear
            :active="loading"
            indeterminate
            color="primary"
            absolute
            top
          />

          <v-toolbar color="primary" dark flat class="rounded-t-lg">
            <v-toolbar-title class="text-h6 font-weight-medium">Create Account</v-toolbar-title>
          </v-toolbar>

          <v-card-text class="pa-6">
            <v-form @submit.prevent="handleRegister">
              <v-alert
                v-if="apiErrorMessages.length > 0"
                type="error"
                variant="tonal"
                closable
                density="compact"
                class="mb-5"
                @update:modelValue="clearApiErrorMessages"
                title="Registration Error"
              >
                <div
                  v-for="(msg, index) in apiErrorMessages"
                  :key="index"
                  class="text-caption"
                >
                  {{ msg }}
                </div>
              </v-alert>

              <v-text-field
                v-model="v$.username.$model"
                label="Username*"
                required
                variant="outlined"
                class="mb-4"
                :error-messages="v$.username.$errors.map(e => e.$message)"
                @blur="v$.username.$touch()"
                color="primary"
                density="comfortable"
                prepend-inner-icon="mdi-account-outline"
              />

              <v-text-field
                v-model="v$.email.$model"
                label="Email*"
                type="email"
                required
                variant="outlined"
                class="mb-4"
                :error-messages="v$.email.$errors.map(e => e.$message)"
                @blur="v$.email.$touch()"
                color="primary"
                density="comfortable"
                prepend-inner-icon="mdi-email-outline"
              />

              <v-text-field
                v-model="v$.password.$model"
                label="Password*"
                type="password"
                required
                variant="outlined"
                class="mb-4"
                :error-messages="v$.password.$errors.map(e => e.$message)"
                @blur="v$.password.$touch()"
                hint="Minimum 8 characters"
                persistent-hint
                color="primary"
                density="comfortable"
                prepend-inner-icon="mdi-lock-outline"
              />

              <v-text-field
                v-model="v$.confirmPassword.$model"
                label="Confirm Password*"
                type="password"
                required
                variant="outlined"
                class="mb-4"
                :error-messages="v$.confirmPassword.$errors.map(e => e.$message)"
                @blur="v$.confirmPassword.$touch()"
                color="primary"
                density="comfortable"
                prepend-inner-icon="mdi-lock-check-outline"
              />

              <v-text-field
                v-model="formData.first_name"
                label="First Name (Optional)"
                variant="outlined"
                class="mb-4"
                color="primary"
                density="comfortable"
                prepend-inner-icon="mdi-account-details-outline"
              />

              <v-text-field
                v-model="formData.last_name"
                label="Last Name (Optional)"
                variant="outlined"
                class="mb-4"
                color="primary"
                density="comfortable"
                prepend-inner-icon="mdi-account-details-outline"
              />

              <v-card-actions class="pa-0 mt-3 d-flex justify-space-between align-center">
                <router-link :to="{ name: 'Login' }" class="text-caption account-link">
                  Already have an account? Login
                </router-link>

                <v-btn
                  type="submit"
                  color="primary"
                  :loading="loading"
                  :disabled="v$.$invalid || loading"
                  size="large"
                  variant="flat"
                  class="register-button font-weight-bold"
                >
                  Register
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
import { required, email, minLength, sameAs, helpers } from '@vuelidate/validators';
import { registerUserApi } from '@/services/authService';

const emit = defineEmits(['registration-success', 'registration-failure']);

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  first_name: '',
  last_name: ''
});

const loading = ref(false);
const apiErrorMessages = ref([]);

const passwordValue = computed(() => formData.password);

const rules = computed(() => ({
  username: { required: helpers.withMessage('Username is required', required) },
  email: {
    required: helpers.withMessage('Email is required', required),
    email: helpers.withMessage('Invalid email format', email)
  },
  password: {
    required: helpers.withMessage('Password is required', required),
    minLength: helpers.withMessage('Password must be at least 8 characters', minLength(8))
  },
  confirmPassword: {
    required: helpers.withMessage('Confirm Password is required', required),
    sameAsPassword: helpers.withMessage('Passwords do not match', sameAs(passwordValue))
  },
  first_name: {},
  last_name: {}
}));

const v$ = useVuelidate(rules, formData);

const handleRegister = async () => {
  const isValid = await v$.value.$validate();
  if (!isValid) return;

  loading.value = true;
  apiErrorMessages.value = [];

  const payload = {
    username: formData.username,
    email: formData.email,
    password: formData.password,
    profile: { // Assuming your backend expects profile data nested for first/last name
        first_name: formData.first_name || undefined,
        last_name: formData.last_name || undefined
    }
  };

  if (!payload.profile.first_name) delete payload.profile.first_name;
  if (!payload.profile.last_name) delete payload.profile.last_name;
  if (Object.keys(payload.profile).length === 0) delete payload.profile;


  try {
    await registerUserApi(payload);
    emit('registration-success');
  } catch (error) {
    if (Array.isArray(error)) {
      apiErrorMessages.value = error;
    } else if (error && error.message) {
      apiErrorMessages.value = [error.message];
    } else {
      apiErrorMessages.value = ['An unexpected error occurred. Please try again.'];
    }
    emit('registration-failure', error);
  } finally {
    loading.value = false;
  }
};

const clearApiErrorMessages = () => {
  apiErrorMessages.value = [];
};
</script>

<style lang="scss" scoped>
.fill-height {
  min-height: 100vh;
}
.themed-background {
}
.register-card {
  border-radius: 12px;
}
.v-toolbar-title {
  color: rgb(var(--v-theme-on-primary));
}
.account-link {
  color: rgba(var(--v-theme-on-surface-rgb), 0.7);
  text-decoration: none;
  transition: color 0.2s ease-in-out;
  &:hover {
    color: rgb(var(--v-theme-primary));
    text-decoration: underline;
  }
}
.register-button {
  color: rgb(var(--v-theme-on-primary));
  min-width: 120px;
}
</style>