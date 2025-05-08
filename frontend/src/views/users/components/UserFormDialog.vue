<template>
    <v-dialog :model-value="modelValue" @update:model-value="closeInternally" persistent max-width="550px" @keydown.esc="closeInternally">
      <v-card :loading="formSubmitting" :color="$vuetify.theme.current.colors.surface">
        <v-toolbar color="primary" flat>
          <v-toolbar-title class="text-h6 font-weight-medium">{{ isEditing ? 'Edit User' : 'Create New User' }}</v-toolbar-title>
          <v-spacer />
          <v-btn icon="mdi-close" @click="closeInternally" variant="text" />
        </v-toolbar>
        <v-card-text class="pt-6 pb-4 px-6">
          <v-alert
            v-if="formError"
            type="error" variant="tonal" closable density="compact" class="mb-5"
            title="Error"
            @update:modelValue="clearFormError"
          >
            {{ formError }}
          </v-alert>
          <v-form ref="userFormRef" @submit.prevent="saveUserInternal">
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.username"
                  label="Username*"
                  variant="outlined" density="comfortable"
                  :rules="[rules.required, rules.username]"
                  required color="primary"
                  prepend-inner-icon="mdi-account-outline"
                  :disabled="isEditing"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.email"
                  label="Email*"
                  type="email"
                  variant="outlined" density="comfortable"
                  :rules="[rules.required, rules.email]"
                  required color="primary"
                  prepend-inner-icon="mdi-email-outline"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.first_name"
                  label="First Name"
                  variant="outlined" density="comfortable" color="primary"
                  prepend-inner-icon="mdi-account-details-outline"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.last_name"
                  label="Last Name"
                  variant="outlined" density="comfortable" color="primary"
                  prepend-inner-icon="mdi-account-details-outline"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.role"
                  label="Role*"
                  :items="availableRoles"
                  item-title="title" item-value="value"
                  variant="outlined" density="comfortable"
                  :rules="[rules.required]"
                  required color="primary"
                  prepend-inner-icon="mdi-account-star-outline"
                />
              </v-col>
              <template v-if="!isEditing">
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="form.password"
                    label="Password*"
                    type="password"
                    variant="outlined" density="comfortable"
                    :rules="[rules.required, rules.password]"
                    required color="primary"
                    autocomplete="new-password"
                    prepend-inner-icon="mdi-lock-outline"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="form.passwordConfirm"
                    label="Confirm Password*"
                    type="password"
                    variant="outlined" density="comfortable"
                    :rules="[rules.required, v => v === form.password || 'Passwords do not match']"
                    required color="primary"
                    autocomplete="new-password"
                    prepend-inner-icon="mdi-lock-check-outline"
                  />
                </v-col>
              </template>
            </v-row>
          </v-form>
          <small class="text-caption text-disabled mt-1 d-block">* Indicates required field</small>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="closeInternally" :disabled="formSubmitting" class="data-table-secondary-text">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveUserInternal" :loading="formSubmitting" class="add-user-btn font-weight-bold">{{ isEditing ? 'Save Changes' : 'Create User' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref, reactive, computed, watch, onMounted } from 'vue';
  import { createUserApi, updateUserApi, updateUserRole, fetchUserById } from '@/services/userService';
  import { roleChoicesForSelect } from '@/lib/choices'; // Assuming this path is correct
  
  const props = defineProps({
    modelValue: Boolean,
    userIdToEdit: {
      type: [String, Number, null],
      default: null,
    },
  });
  
  const emit = defineEmits(['update:modelValue', 'saved']);
  
  const userFormRef = ref(null);
  const formSubmitting = ref(false);
  const formError = ref(null);
  const originalUserData = ref(null);
  
  const form = reactive({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: null,
    password: '',
    passwordConfirm: ''
  });
  
  const isEditing = computed(() => !!props.userIdToEdit);
  const availableRoles = computed(() => roleChoicesForSelect);
  
  const rules = {
    required: value => !!value || 'Required.',
    email: value => /.+@.+\..+/.test(value) || 'E-mail must be valid.',
    username: value => (value && value.length >= 3) || 'Min 3 characters.',
    password: value => (value && value.length >= 8) || 'Min 8 characters.',
  };
  
  const resetForm = () => {
    form.username = '';
    form.email = '';
    form.first_name = '';
    form.last_name = '';
    form.role = null;
    form.password = '';
    form.passwordConfirm = '';
    originalUserData.value = null;
    userFormRef.value?.resetValidation();
    formError.value = null;
  };
  
  const populateFormForEdit = async (userId) => {
    if (!userId) return;
    formSubmitting.value = true;
    formError.value = null;
    try {
      const userData = await fetchUserById(userId);
      originalUserData.value = { ...userData, profile: { ...userData.profile }};
      form.username = userData.username;
      form.email = userData.email;
      form.first_name = userData.first_name || '';
      form.last_name = userData.last_name || '';
      form.role = userData.profile?.role || null;
    } catch (err) {
      console.error("Failed to load user for editing:", err);
      let errorMessage = "Could not load user data for editing.";
      if (err?.detail) errorMessage = err.detail;
      else if (typeof err === 'string') errorMessage = err;
      else if (err?.message) errorMessage = err.message;
      formError.value = errorMessage;
    } finally {
      formSubmitting.value = false;
    }
  };
  
  watch(() => props.modelValue, (newValue) => {
    if (newValue) {
      resetForm();
      if (isEditing.value && props.userIdToEdit) {
        populateFormForEdit(props.userIdToEdit);
      }
    }
  });
  
  onMounted(() => {
    if (props.modelValue && isEditing.value && props.userIdToEdit) {
      populateFormForEdit(props.userIdToEdit);
    }
  });
  
  const closeInternally = (value = false) => {
    emit('update:modelValue', typeof value === 'boolean' ? value : false);
  };
  
  const clearFormError = () => {
    formError.value = null;
  };
  
  const saveUserInternal = async () => {
    const { valid } = await userFormRef.value?.validate();
    if (!valid) return;
  
    formSubmitting.value = true;
    formError.value = null;
  
    try {
      if (isEditing.value) {
        if (!props.userIdToEdit || !originalUserData.value) return;
  
        const detailsPayload = {};
        // Username is disabled for editing, so no need to compare
        // if (form.username !== originalUserData.value.username) detailsPayload.username = form.username;
        if (form.email !== originalUserData.value.email) detailsPayload.email = form.email;
        
        // Only include first_name/last_name if they've changed from the original,
        // or if they were originally null/empty and now have a value.
        // Send undefined to let backend potentially clear it, or '' if backend expects empty string.
        // updateUserApi in userService.js now handles deleting keys if value is ''.
        if (form.first_name !== (originalUserData.value.first_name || '')) detailsPayload.first_name = form.first_name;
        if (form.last_name !== (originalUserData.value.last_name || '')) detailsPayload.last_name = form.last_name;
  
  
        if (Object.keys(detailsPayload).length > 0) {
          await updateUserApi(props.userIdToEdit, detailsPayload);
        }
  
        if (originalUserData.value.profile?.role !== form.role && form.role) {
          await updateUserRole(props.userIdToEdit, form.role);
        }
      } else {
        const createPayload = {
          username: form.username,
          email: form.email,
          first_name: form.first_name || undefined,
          last_name: form.last_name || undefined,
          password: form.password,
          profile_attributes: { role: form.role }
        };
        if (!createPayload.first_name) delete createPayload.first_name;
        if (!createPayload.last_name) delete createPayload.last_name;
        if (!createPayload.profile_attributes.role) delete createPayload.profile_attributes;
        
        await createUserApi(createPayload);
      }
      emit('saved');
      closeInternally(false);
    } catch (err) {
      let errorMessage = 'Operation failed.';
      if (err?.detail) errorMessage = err.detail;
      else if (typeof err === 'string') errorMessage = err;
      else if (Array.isArray(err) && err.length > 0 && typeof err[0] === 'string') errorMessage = err.join('; ');
      else if (err?.message) errorMessage = err.message;
      else if (typeof err === 'object' && err !== null) {
          const messages = Object.values(err).flat().filter(m => typeof m === 'string');
          if (messages.length > 0) errorMessage = messages.join('; ');
      }
      formError.value = errorMessage;
      console.error(`Failed to ${isEditing.value ? 'update' : 'create'} user:`, err);
    } finally {
      formSubmitting.value = false;
    }
  };
  </script>
  
  <style scoped lang="scss">
  .data-table-secondary-text {
    color: rgba(var(--v-theme-on-surface-rgb), 0.75);
      &:hover {
        color: rgb(var(--v-theme-on-surface));
      }
  }
  .add-user-btn {
    color: rgb(var(--v-theme-on-primary));
  }
  :deep(.v-dialog .v-toolbar-title) {
      color: rgb(var(--v-theme-on-primary));
  }
  :deep(.v-dialog small.text-disabled) {
      color: rgba(var(--v-theme-on-surface-rgb), 0.6) !important;
  }
  </style>