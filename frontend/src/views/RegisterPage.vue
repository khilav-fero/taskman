<template>
    <v-container class="fill-height" fluid>
      <v-row align-items="center" justify="center">
        <v-col cols="12" sm="8" md="6" lg="4">
          <v-card class="elevation-12">
             <v-progress-linear
              :active="authStore.getLoading"
              indeterminate
              color="secondary"
              absolute
              top
            ></v-progress-linear>
  
            <v-toolbar color="secondary" dark flat>
              <v-toolbar-title>Register</v-toolbar-title>
            </v-toolbar>
  
            <v-card-text class="pt-4">
              <v-form @submit.prevent="handleRegister">
                 <v-alert
                  v-if="authStore.getError"
                  type="error"
                  variant="tonal"
                  closable
                  density="compact"
                  class="mb-4"
                  @update:modelValue="clearError"
                  :title="formattedErrorTitle"
                 >
                   <div v-for="(msg, index) in formattedErrorMessages" :key="index" class="text-caption">
                      {{ msg }}
                   </div>
                </v-alert>
  
                <v-text-field
                  v-model="v$.username.$model" label="Username" required variant="outlined" class="mb-2"
                  :error-messages="v$.username.$errors.map(e => e.$message)" @blur="v$.username.$touch()"
                ></v-text-field>
  
                <v-text-field
                  v-model="v$.email.$model" label="Email" type="email" required variant="outlined" class="mb-2"
                  :error-messages="v$.email.$errors.map(e => e.$message)" @blur="v$.email.$touch()"
                ></v-text-field>
  
                <v-text-field
                  v-model="v$.password.$model" label="Password" type="password" required variant="outlined" class="mb-2"
                  :error-messages="v$.password.$errors.map(e => e.$message)" @blur="v$.password.$touch()"
                  hint="Minimum 8 characters" persistent-hint
                ></v-text-field>
  
                 <v-text-field
                  v-model="v$.confirmPassword.$model" label="Confirm Password" type="password" required variant="outlined" class="mb-2"
                  :error-messages="v$.confirmPassword.$errors.map(e => e.$message)" @blur="v$.confirmPassword.$touch()"
                ></v-text-field>
  
                 <v-text-field v-model="formData.first_name" label="First Name (Optional)" variant="outlined" class="mb-2"></v-text-field>
                 <v-text-field v-model="formData.last_name" label="Last Name (Optional)" variant="outlined" class="mb-2"></v-text-field>
  
                <v-card-actions class="pa-0 mt-2">
                   <router-link :to="{ name: 'Login' }" class="text-body-2 ml-1">
                     Have an account?
                   </router-link>
                   <v-spacer></v-spacer>
                   <v-btn
                     type="submit" color="secondary" :loading="authStore.getLoading"
                     :disabled="v$.$invalid || authStore.getLoading" size="large" variant="elevated"
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
  import { useAuthStore } from '@/store/auth';
  import { useVuelidate } from '@vuelidate/core';
  import { required, email, minLength, sameAs, helpers } from '@vuelidate/validators';
  
  const authStore = useAuthStore();
  
  const formData = reactive({
    username: '', email: '', password: '', confirmPassword: '',
    first_name: '', last_name: '',
  });
  
  const passwordValue = computed(() => formData.password); 

  const rules = computed(() => ({
    username: { required: helpers.withMessage('Username is required', required) },
    email: {
      required: helpers.withMessage('Email is required', required),
      email: helpers.withMessage('Invalid email format', email),
    },
    password: {
      required: helpers.withMessage('Password is required', required),
      minLength: helpers.withMessage('Password needs 8+ characters', minLength(8)),
    },
    confirmPassword: {
      required: helpers.withMessage('Confirm Password is required', required),
      sameAsPassword: helpers.withMessage('Passwords do not match', sameAs(passwordValue)), // FIXED
    },
    first_name: {},
    last_name: {},
  }));

  
  const v$ = useVuelidate(rules, formData); // No toRefs needed
  
  const formattedErrorMessages = computed(() => {
      const error = authStore.getError;
      if (!error) return [];
      if (error.startsWith('Registration failed: ')) {
          return error.substring('Registration failed: '.length).split('; ').map(e => e.trim()).filter(Boolean);
      }
      return [error];
  });
  
  const formattedErrorTitle = computed(() => {
     return authStore.getError ? 'Registration Error' : '';
  });
  
  const handleRegister = async () => {
    const isValid = await v$.value.$validate();
    if (!isValid) return;
  
    const payload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name || '',
        last_name: formData.last_name || '',
    };
    await authStore.register(payload);
  };
  
  const clearError = () => {
      authStore.error = null;
  }
  </script>
  
  <style scoped>
   .fill-height { min-height: 90vh; }
  </style>