<template>
  <v-card :loading="loading || usersLoadingInitial" :color="$vuetify.theme.current.colors.surface" rounded="lg">
    <v-toolbar color="primary" density="compact" flat>
      <v-toolbar-title class="text-h6 font-weight-medium">{{ formTitle }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-close" variant="text" @click="cancelForm" :disabled="loading"></v-btn>
    </v-toolbar>

    <v-card-text class="pt-6 pb-2">
      <v-form ref="vuetifyFormRef" @submit.prevent="submitForm">
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
                counter maxlength="200"
                color="primary"
                class="form-field-themed"
                autofocus
                :error-messages="v$.formData.title.$errors.map(e => e.$message)"
                @blur="v$.formData.title.$touch()"
                @input="v$.formData.title.$validate()"
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="formData.description"
                label="Description" variant="outlined" rows="3" density="comfortable"
                counter
                color="primary"
                class="form-field-themed"
                :error-messages="v$.formData.description.$errors.map(e => e.$message)"
                @blur="v$.formData.description.$touch()"
                @input="v$.formData.description.$validate()"
              />
            </v-col>

            <v-col cols="12" sm="6">
               <v-select
                  v-model="formData.status"
                  :items="taskStatusChoices" item-title="title" item-value="value"
                  label="Status*" variant="outlined" density="comfortable"
                  color="primary"
                  class="form-field-themed"
                  prepend-inner-icon="mdi-list-status"
                  :error-messages="v$.formData.status.$errors.map(e => e.$message)"
                  @blur="v$.formData.status.$touch()"
                  @update:modelValue="v$.formData.status.$validate()"
              />
            </v-col>

            <v-col cols="12" sm="6">
               <v-select
                  v-model="formData.priority"
                  :items="taskPriorityChoices" item-title="title" item-value="value"
                  label="Priority*" variant="outlined" density="comfortable"
                  color="primary"
                  class="form-field-themed"
                  prepend-inner-icon="mdi-priority-high"
                  :error-messages="v$.formData.priority.$errors.map(e => e.$message)"
                  @blur="v$.formData.priority.$touch()"
                  @update:modelValue="v$.formData.priority.$validate()"
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
                  :error-messages="v$.formData.assignee_id.$errors.map(e => e.$message)"
                  @blur="v$.formData.assignee_id.$touch()"
                  @update:modelValue="v$.formData.assignee_id.$validate()"
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
                  @update:model-value="v$.formData.deadline.$touch(); v$.formData.deadline.$validate()"
                  @closed="v$.formData.deadline.$touch()"
              />
              <div v-if="v$.formData.deadline.$errors.length" class="v-input__details" style="padding-inline-start: 16px; padding-inline-end: 16px;">
                <div class="v-messages">
                  <div v-for="errorMsg in v$.formData.deadline.$errors" :key="errorMsg.$uid" class="v-messages__message text-error">
                    {{ errorMsg.$message }}
                  </div>
                </div>
              </div>
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

<script>
import { taskStatusChoices, taskPriorityChoices } from '@/lib/choices';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { fetchAllUsers } from '@/services/userService';
import { useVuelidate } from '@vuelidate/core';
import { required, maxLength, helpers } from '@vuelidate/validators';

export default {
  name: 'TaskForm',
  components: {
    VueDatePicker
  },
  props: {
    initialData: { type: Object, default: null },
    loading: { type: Boolean, default: false },
    error: { type: String, default: null }
  },
  emits: ['submit', 'cancel', 'clear-form-error'],
  data() {
    return {
      v$: useVuelidate(),
      formData: this._defaultFormData(),
      assignableUsers: [],
      usersLoading: false,
      usersLoadingInitial: true,
      taskStatusChoices: taskStatusChoices,
      taskPriorityChoices: taskPriorityChoices,
    };
  },
  validations() {
    return {
      formData: {
        title: {
          required: helpers.withMessage('Title is required.', required),
          maxLength: helpers.withMessage('Title cannot exceed 200 characters.', maxLength(200))
        },
        description: {
          maxLength: helpers.withMessage('Description cannot exceed 1000 characters.', maxLength(1000))
        },
        status: {
          required: helpers.withMessage('Status is required.', required)
        },
        priority: {
          required: helpers.withMessage('Priority is required.', required)
        },
        assignee_id: {},
        deadline: {
          isValidDateOrNull: helpers.withMessage('Please select a valid date.', this.isValidDateOrNull)
        }
      }
    };
  },
  computed: {
    isDark() {
      return this.$vuetify.theme.current.dark;
    },
    isEditMode() {
      return this.initialData && this.initialData.id;
    },
    formTitle() {
      return this.isEditMode ? 'Edit Task' : 'Create New Task';
    }
  },
  watch: {
    initialData: {
      handler(newData) {
        this.populateForm(newData);
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    _defaultFormData() {
      return {
        title: '',
        description: '',
        status: 'TODO',
        priority: 2,
        deadline: null,
        assignee_id: null,
      };
    },
    isValidDateOrNull(value) {
      if (value === null || value === undefined || value === '') return true;
      return !isNaN(new Date(value).getTime());
    },
    async loadUsers() {
      this.usersLoading = true;
      if (this.assignableUsers.length === 0) {
        this.usersLoadingInitial = true;
      }
      try {
        const response = await fetchAllUsers();
        if (response && Array.isArray(response.results)) {
          this.assignableUsers = response.results;
        } else if (Array.isArray(response)) {
          this.assignableUsers = response;
        } else {
          this.assignableUsers = [];
          console.warn("TaskForm: fetchAllUsers did not return expected 'results' array EXPLICIT ERROR WITH TASKFORM.");
        }
      } catch (error) {
        console.error("TaskForm: Failed to load users for assignee select:", error);
        this.assignableUsers = [];
      } finally {
        this.usersLoading = false;
        this.usersLoadingInitial = false;
      }
    },
    resetForm() {
      this.formData = this._defaultFormData();
      if (this.v$) {
        this.v$.$reset();
      }
      if (this.$refs.vuetifyFormRef) {
        this.$refs.vuetifyFormRef.resetValidation();
      }
    },
    populateForm(newData) {
      if (newData && newData.id) {
        this.formData.title = newData.title || '';
        this.formData.description = newData.description || '';
        this.formData.status = newData.status || 'TODO';
        this.formData.priority = newData.priority || 2;
        this.formData.deadline = newData.deadline ? new Date(newData.deadline + 'T00:00:00Z') : null;
        this.formData.assignee_id = newData.assignee_id || newData.assignee?.id || null;
      } else {
        this.formData = this._defaultFormData();
      }
      if (this.v$) {
        this.v$.$reset();
      }
    },
    async submitForm() {
      this.v$.$touch();
      const isFormValid = await this.v$.$validate();

      if (!isFormValid) {
        if (this.$refs.vuetifyFormRef) {
            await this.$refs.vuetifyFormRef.validate();
        }
        return;
      }

      const payload = {
          title: this.formData.title,
          description: this.formData.description || null,
          status: this.formData.status,
          priority: this.formData.priority,
          assignee_id: this.formData.assignee_id || null,
      };

      if (this.formData.deadline instanceof Date && !isNaN(this.formData.deadline.getTime())) {
          try {
              const year = this.formData.deadline.getFullYear();
              const month = (this.formData.deadline.getMonth() + 1).toString().padStart(2, '0');
              const day = this.formData.deadline.getDate().toString().padStart(2, '0');
              payload.deadline = `${year}-${month}-${day}`;
          } catch (e) { payload.deadline = null; }
      } else if (this.formData.deadline === null || this.formData.deadline === '') {
          payload.deadline = null;
      } else {
          payload.deadline = this.formData.deadline;
      }
      this.$emit('submit', payload);
    },
    cancelForm() {
      this.resetForm();
      this.$emit('cancel');
    }
  },
  mounted() {
    this.loadUsers();
    if (!this.initialData) {
       this.formData = this._defaultFormData();
    }
  }
};
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
  &.v-input--is-focused .v-field__outline,
  &.v-input--error:not(.v-input--disabled) .v-field__outline {
    border-color: rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12) !important;
  }
   &.v-input--error:not(.v-input--disabled) .v-field__outline{
    border-color: rgb(var(--v-theme-error)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-error-rgb), 0.12) !important;
  }

  .v-label.v-field-label {
    color: rgba(var(--v-theme-on-surface), 0.65) !important;
    font-weight: 400;
  }
  &.v-input--is-focused .v-label.v-field-label,
  .v-field--active .v-label.v-field-label {
    color: rgb(var(--v-theme-primary)) !important;
  }
   &.v-input--error:not(.v-input--disabled) .v-label.v-field-label{
     color: rgb(var(--v-theme-error)) !important;
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
.dp-custom-input:focus, .dp-custom-input.dp__input_focus,
.dp-custom-input.dp__input_invalid {
  border-color: rgb(var(--v-theme-primary)) !important;
  box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12) !important;
  outline: none;
}
.dp-custom-input.dp__input_invalid {
    border-color: rgb(var(--v-theme-error)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-error-rgb), 0.12) !important;
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
.v-theme--dark .dp-custom-input:focus, .v-theme--dark .dp-custom-input.dp__input_focus,
.v-theme--dark .dp-custom-input.dp__input_invalid {
    border-color: rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12) !important;
}
.v-theme--dark .dp-custom-input.dp__input_invalid {
    border-color: rgb(var(--v-theme-error)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-error-rgb), 0.12) !important;
}

.add-user-btn {
  color: rgb(var(--v-theme-on-primary));
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
    background-color: rgba(var(--v-theme-on-surface), 0.05);
  }
}
</style>