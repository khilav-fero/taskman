<template>
    <v-dialog :model-value="modelValue" @update:model-value="closeInternally" persistent max-width="450px" @keydown.esc="closeInternally">
      <v-card :loading="submitting" :color="$vuetify.theme.current.colors.surface">
        <v-card-title class="text-h5 font-weight-medium d-flex align-center" :style="{ color: $vuetify.theme.current.colors.error }">
          <v-icon start :color="$vuetify.theme.current.colors.error">mdi-alert-circle-outline</v-icon>
          Confirm Deletion
        </v-card-title>
        <v-card-text class="py-4 data-table-primary-text">
          Are you sure you want to permanently delete the user:
          <br />
          <strong class="text-subtitle-1 my-1 d-block">{{ userToDelete?.username }}</strong>
          <br />
          <strong :style="{ color: $vuetify.theme.current.colors.error }">This action cannot be undone.</strong>
          <v-alert
            v-if="error"
            type="error" variant="tonal" closable density="compact" class="mt-4"
            title="Error"
            @update:modelValue="clearError"
          >
            {{ error }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="pa-3">
          <v-spacer />
          <v-btn variant="text" @click="closeInternally" :disabled="submitting" class="data-table-secondary-text">Cancel</v-btn>
          <v-btn color="error" variant="flat" @click="confirmDeleteInternal" :loading="submitting" class="font-weight-bold">Delete User</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { deleteUserApi } from '@/services/userService';
  
  const props = defineProps({
    modelValue: Boolean,
    userToDelete: {
      type: Object,
      default: null,
    },
  });
  
  const emit = defineEmits(['update:modelValue', 'confirmed', 'error']);
  
  const submitting = ref(false);
  const error = ref(null);
  
  const closeInternally = (value = false) => {
    emit('update:modelValue', typeof value === 'boolean' ? value : false);
    if (!value) {
      error.value = null;
    }
  };
  
  const clearError = () => {
    error.value = null;
  };
  
  const confirmDeleteInternal = async () => {
    if (!props.userToDelete?.id) return;
    submitting.value = true;
    error.value = null;
    try {
      await deleteUserApi(props.userToDelete.id);
      emit('confirmed');
      closeInternally(false);
    } catch (err) {
      let errorMessage = 'Failed to delete user.';
      if (err?.detail) errorMessage = err.detail;
      else if (typeof err === 'string') errorMessage = err;
      else if (err?.message) errorMessage = err.message;
      error.value = errorMessage;
      emit('error', error.value);
      console.error("Failed to delete user:", err);
    } finally {
      submitting.value = false;
    }
  };
  </script>
  
  <style scoped lang="scss">
  .data-table-primary-text {
      color: rgb(var(--v-theme-on-surface));
      line-height: 1.5;
  }
  .data-table-secondary-text {
    color: rgba(var(--v-theme-on-surface-rgb), 0.75);
      &:hover {
        color: rgb(var(--v-theme-on-surface));
      }
  }
  </style>