<template>
    <v-dialog :model-value="modelValue" @update:model-value="closeInternally" persistent max-width="450px" @keydown.esc="closeInternally">
      <v-card :loading="submitting" :color="$vuetify.theme.current.colors.surface" rounded="lg">
        <v-card-title class="text-h5 font-weight-medium d-flex align-center dialog-title-error">
          <v-icon start class="dialog-title-icon">mdi-alert-circle-outline</v-icon>
          Confirm Deletion
        </v-card-title>
        <v-card-text class="py-4 dialog-text-primary">
          Are you sure you want to permanently delete the task:
          <br />
          <strong class="text-subtitle-1 my-1 d-block">{{ taskToDelete?.title }}</strong>
          <br />
          <strong :style="{ color: $vuetify.theme.current.colors.error }">This action cannot be undone.</strong>
          <v-alert
            v-if="error"
            type="error" variant="tonal" closable density="compact" class="mt-4"
            border="start"
            elevation="2"
            prominent
            icon="mdi-alert-circle-outline"
            title="Error"
            @update:modelValue="clearError"
          >
            {{ error }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="pa-4 dialog-actions">
          <v-spacer />
          <v-btn variant="text" @click="closeInternally" :disabled="submitting" class="dialog-btn-cancel">Cancel</v-btn>
          <v-btn color="error" variant="flat" @click="confirmDeleteInternal" :loading="submitting" class="font-weight-bold dialog-btn-confirm">Delete Task</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { deleteTaskApi as deleteTaskServiceApi } from '@/services/taskService';
  
  const props = defineProps({
    modelValue: Boolean,
    taskToDelete: {
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
    if (!props.taskToDelete?.id) return;
    submitting.value = true;
    error.value = null;
    try {
      await deleteTaskServiceApi(props.taskToDelete.id);
      emit('confirmed');
      closeInternally(false);
    } catch (err) {
      let errorMessage = 'Failed to delete task.';
      if (err?.detail) errorMessage = err.detail;
      else if (typeof err === 'string') errorMessage = err;
      else if (err?.message) errorMessage = err.message;
      error.value = errorMessage;
      emit('error', error.value);
      console.error("Failed to delete task:", err);
    } finally {
      submitting.value = false;
    }
  };
  </script>
  
  <style lang="scss" scoped>
  .dialog-title-error {
    color: rgb(var(--v-theme-error)) !important;
  }
  .dialog-title-icon {
     color: rgb(var(--v-theme-error)) !important;
  }
  .dialog-text-primary {
    color: rgb(var(--v-theme-on-surface));
    line-height: 1.6;
    strong {
      color: rgb(var(--v-theme-on-surface));
      font-weight: 500;
    }
  }
  .dialog-actions {
    background-color: rgba(var(--v-theme-on-surface), 0.03);
    border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  }
  .dialog-btn-cancel {
    color: rgba(var(--v-theme-on-surface), 0.75);
    font-weight: 500;
    &:hover {
      color: rgb(var(--v-theme-on-surface));
    }
  }
  .dialog-btn-confirm {
    color: rgb(var(--v-theme-on-error)) !important;
    font-weight: 500;
  }
  </style>