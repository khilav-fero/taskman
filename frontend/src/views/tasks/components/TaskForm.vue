<template>
  <v-card :loading="loading || usersLoadingInitial" :color="$vuetify.theme.current.colors.surface" rounded="lg">
    <v-toolbar color="primary" density="compact" flat>
      <v-toolbar-title class="text-h6 font-weight-medium">{{ formTitle }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-close" variant="text" @click="cancelForm" :disabled="loading"></v-btn>
    </v-toolbar>

    <v-card-text class="pt-6 pb-2">
      <v-form ref="formRef" @submit.prevent="submitForm">
        <v-container class="pa-0">
          <v-alert
            v-if="error"
            type="error" variant="tonal" density="compact" class="mb-5"
            closable @update:modelValue="$emit('clear-form-error')"
            border="start"
            elevation="2"
            prominent
            icon="mdi-alert-circle-outline"
            title="Form Error"
          >
            {{ error }}
          </v-alert>

          <v-row dense>
            <v-col cols="12">
              <v-text-field
                v-model="formData.title"
                label="Title*"
                variant="outlined" density="comfortable"
                :rules="[rules.required, rules.maxLength(200)]"
                counter maxlength="200"
                color="primary"
                class="form-field-themed"
                autofocus
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="formData.description"
                label="Description" variant="outlined" rows="3" density="comfortable"
                counter
                color="primary"
                class="form-field-themed"
              />
            </v-col>

            <v-col cols="12" sm="6">
               <v-select
                  v-model="formData.status"
                  :items="taskStatusChoices" item-title="title" item-value="value"
                  label="Status*" variant="outlined" required density="comfortable"
                  :rules="[rules.required]"
                  color="primary"
                  class="form-field-themed"
                  prepend-inner-icon="mdi-list-status"
              />
            </v-col>

            <v-col cols="12" sm="6">
               <v-select
                  v-model="formData.priority"
                  :items="taskPriorityChoices" item-title="title" item-value="value"
                  label="Priority*" variant="outlined" required density="comfortable"
                  :rules="[rules.required]"
                  color="primary"
                  class="form-field-themed"
                  prepend-inner-icon="mdi-priority-high"
              />
            </v-col>

            <v-col cols="12" sm="6">
               <v-autocomplete
                  v-model="formData.assignee_id"
                  :items="assignableUsers"
                  item-title="username"
                  item-value="id"
                  label="Assignee (Optional)"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  :loading="usersLoading"
                  no-data-text="No users available or found"
                  color="primary"
                  class="form-field-themed"
                  prepend-inner-icon="mdi-account-outline"
               />
            </v-col>

            <v-col cols="12" sm="6">
              <VueDatePicker
                  v-model="formData.deadline"
                  placeholder="Select Deadline (Optional)"
                  :enable-time-picker="false"
                  :clearable="true"
                  format="yyyy-MM-dd"
                  :teleport="true"
                  auto-apply
                  input-class-name="dp-custom-input form-field-themed"
                  :dark="isDark"
                  :prevent-min-max-navigation="true"
                  :month-change-on-scroll="false"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions class="pa-4 dialog-actions">
      <v-spacer />
      <v-btn class="dialog-btn-cancel" variant="text" @click="cancelForm" :disabled="loading">
        Cancel
      </v-btn>
      <v-btn color="primary" variant="flat" @click="submitForm" :loading="loading" class="font-weight-bold add-user-btn">
        {{ isEditMode ? 'Save Changes' : 'Create Task' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { taskStatusChoices, taskPriorityChoices } from '@/lib/choices';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { useTheme } from 'vuetify';
import { fetchAllUsers } from '@/services/userService';

const props = defineProps({
  initialData: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null }
});

const emit = defineEmits(['submit', 'cancel', 'clear-form-error']);

const theme = useTheme();
const isDark = computed(() => theme.global.current.value.dark);

const formRef = ref(null);
const assignableUsers = ref([]);
const usersLoading = ref(false);
const usersLoadingInitial = ref(true);

const defaultFormData = () => ({
  title: '',
  description: '',
  status: 'TODO',
  priority: 2,
  deadline: null,
  assignee_id: null,
});

const formData = reactive(defaultFormData());

const isEditMode = computed(() => props.initialData && props.initialData.id);
const formTitle = computed(() => isEditMode.value ? 'Edit Task' : 'Create New Task');

const rules = {
  required: value => !!value || 'This field is required.',
  maxLength: (len) => (value) => (value || '').length <= len || `Max ${len} characters`,
};

const loadUsers = async () => {
  usersLoading.value = true;
  if (assignableUsers.value.length === 0) {
    usersLoadingInitial.value = true;
  }
  try {
    const response = await fetchAllUsers();
    if (response && Array.isArray(response.results)) {
      assignableUsers.value = response.results;
    } else if (Array.isArray(response)) {
      assignableUsers.value = response;
    } else {
      assignableUsers.value = [];
      console.warn("TaskForm: fetchAllUsers did not return expected 'results' array EXPLICIT ERROR WITH TASKFORM.");
    }
  } catch (error) {
    console.error("TaskForm: Failed to load users for assignee select:", error);
    assignableUsers.value = [];
  } finally {
    usersLoading.value = false;
    usersLoadingInitial.value = false;
  }
};

const resetForm = () => {
  Object.assign(formData, defaultFormData());
  if (formRef.value) {
    formRef.value.resetValidation();
  }
};

const populateForm = (newData) => {
  resetForm();
  if (newData && newData.id) {
    formData.title = newData.title || '';
    formData.description = newData.description || '';
    formData.status = newData.status || 'TODO';
    formData.priority = newData.priority || 2;
    formData.deadline = newData.deadline ? new Date(newData.deadline + 'T00:00:00Z') : null;
    formData.assignee_id = newData.assignee?.id || null;
  }
};

watch(() => props.initialData, (newData) => {
  populateForm(newData);
}, { immediate: true, deep: true });

const submitForm = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;

  const payload = {
      title: formData.title,
      description: formData.description || null,
      status: formData.status,
      priority: formData.priority,
      assignee_id: formData.assignee_id || null,
  };

  if (formData.deadline instanceof Date) {
      try {
          const year = formData.deadline.getFullYear();
          const month = (formData.deadline.getMonth() + 1).toString().padStart(2, '0');
          const day = formData.deadline.getDate().toString().padStart(2, '0');
          payload.deadline = `${year}-${month}-${day}`;
      } catch (e) { payload.deadline = null; }
  } else if (formData.deadline === null || formData.deadline === '') {
      payload.deadline = null;
  } else {
      payload.deadline = formData.deadline;
  }
  emit('submit', payload);
};

const cancelForm = () => {
  emit('cancel');
};

onMounted(() => {
  loadUsers();
});
</script>

<style lang="scss">
.form-field-themed {
  .v-field {
    background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
    border-radius: var(--v-border-radius-lg) !important;
  }
  .v-field__outline {
    border-color: rgba(var(--v-theme-on-surface), 0.15) !important;
  }
  &:hover .v-field__outline {
    border-color: rgba(var(--v-theme-on-surface), 0.35) !important;
  }
  &.v-input--is-focused .v-field__outline {
    border-color: rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12) !important;
  }
  .v-label.v-field-label {
    color: rgba(var(--v-theme-on-surface), 0.65) !important;
    font-weight: 400;
  }
  &.v-input--is-focused .v-label.v-field-label,
  .v-field--active .v-label.v-field-label {
    color: rgb(var(--v-theme-primary)) !important;
  }
  input, .v-select__selection-text, .v-textarea__content textarea {
    color: rgb(var(--v-theme-on-surface)) !important;
  }
   .v-field__prepend-inner .v-icon {
    color: rgba(var(--v-theme-on-surface), 0.5) !important;
  }
}

.dp-custom-input {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.15) !important;
  border-radius: var(--v-border-radius-lg) !important;
  padding: 0 12px !important;
  width: 100%;
  box-sizing: border-box;
  font-size: 1rem;
  height: 40px !important;
  line-height: 40px !important;
  background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
  color: rgb(var(--v-theme-on-surface)) !important;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  font-family: inherit;
}
.dp-custom-input:hover {
  border-color: rgba(var(--v-theme-on-surface), 0.35) !important;
}
.dp-custom-input:focus, .dp-custom-input.dp__input_focus {
  border-color: rgb(var(--v-theme-primary)) !important;
  box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12) !important;
  outline: none;
}
.dp-custom-input::placeholder {
  color: rgba(var(--v-theme-on-surface), 0.55);
  opacity: 1;
}
.v-theme--dark .dp-custom-input {
    border-color: rgba(var(--v-theme-on-surface), 0.15) !important;
    background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
    color: rgb(var(--v-theme-on-surface)) !important;
}
.v-theme--dark .dp-custom-input:hover {
    border-color: rgba(var(--v-theme-on-surface), 0.35) !important;
}
.v-theme--dark .dp-custom-input::placeholder {
    color: rgba(var(--v-theme-on-surface), 0.55);
}
.v-theme--dark .dp-custom-input:focus, .v-theme--dark .dp-custom-input.dp__input_focus {
    border-color: rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12) !important;
}

.add-user-btn {
  color: rgb(var(--v-theme-on-primary));
  font-weight: 500;
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
</style>