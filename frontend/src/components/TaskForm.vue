<template>
    <v-card :loading="loading">
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
  
      <v-card-text class="pt-4">
        <v-form ref="formRef">
          <v-container>
            <v-alert
              v-if="error"
              type="error" variant="tonal" density="compact" class="mb-4"
              closable @update:modelValue="$emit('clear-error')"
              title="Error"
            >
              {{ error }}
            </v-alert>
  
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.title"
                  label="Title*"
                  variant="outlined" density="compact"
                  :rules="[rules.required, rules.maxLength(200)]"
                  counter maxlength="200"
                />
              </v-col>
  
              <v-col cols="12">
                <v-textarea
                  v-model="formData.description"
                  label="Description" variant="outlined" rows="3" density="compact"
                  counter
                />
              </v-col>
  
              <!-- Status -->
              <v-col cols="12" sm="6">
                 <v-select
                    v-model="formData.status"
                    :items="taskStatusChoices" item-title="title" item-value="value"
                    label="Status*" variant="outlined" required density="compact"
                    :rules="[rules.required]"
                />
              </v-col>
  
              <!-- Priority -->
              <v-col cols="12" sm="6">
                 <v-select
                    v-model="formData.priority"
                    :items="taskPriorityChoices" item-title="title" item-value="value"
                    label="Priority*" variant="outlined" required density="compact"
                    :rules="[rules.required]"
                />
              </v-col>
  
              <!-- Assignee -->
              <v-col cols="12" sm="6">
                 <v-autocomplete
                    v-model="formData.assignee_id"
                    :items="assignableUsers"
                    item-title="username"
                    item-value="id"
                    label="Assignee (Optional)"
                    variant="outlined"
                    density="compact"
                    clearable
                    :loading="usersLoading"
                    no-data-text="No users found"
                    hide-no-data
                 />
              </v-col>
  
              <!-- Deadline -->
              <v-col cols="12" sm="6">
                <VueDatePicker
                    v-model="formData.deadline"
                    placeholder="Select Deadline (Optional)"
                    :enable-time-picker="false"
                    :clearable="true"
                    format="yyyy-MM-dd"
                    :teleport="true"
                    auto-apply
                    input-class-name="dp-custom-input"
                    :dark="isDark"
                    :prevent-min-max-navigation="true"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
  
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" variant="text" @click="cancelForm" :disabled="loading">
          Cancel
        </v-btn>
        <v-btn color="primary" variant="elevated" @click="submitForm" :loading="loading">
          {{ isEditMode ? 'Save Changes' : 'Create Task' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </template>
  
  <script setup>
  import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue';
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
  
  const emit = defineEmits(['submit', 'cancel', 'clear-error']); 
  
  const theme = useTheme();
  const isDark = computed(() => theme.global.current.value.dark);
  
  const formRef = ref(null); 
  const assignableUsers = ref([]);
  const usersLoading = ref(false);
  
  const formData = reactive({
    title: '', description: '', status: 'TODO', priority: 2, deadline: null,
    assignee_id: null,
  });
  
  const isEditMode = computed(() => props.initialData && props.initialData.id);
  const formTitle = computed(() => isEditMode.value ? 'Edit Task' : 'Create New Task');

  const rules = {
    required: value => !!value || 'This field is required.',
    maxLength: (len) => (value) => (value || '').length <= len || `Max ${len} characters`,
  };
  
  const loadUsers = async () => {
      usersLoading.value = true;
      assignableUsers.value = await fetchAllUsers();
      usersLoading.value = false;
  };
  
  const submitForm = async () => {

      const payload = {
          title: formData.title,
          description: formData.description,
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
      } else {
          payload.deadline = null;
      }
  
      emit('submit', payload);
  };
  
  const cancelForm = () => {
      emit('cancel');
  };
  
  watch(() => props.initialData, (newData) => {
      if (newData && newData.id) {
          formData.title = newData.title || '';
          formData.description = newData.description || '';
          formData.status = newData.status || 'TODO';
          formData.priority = newData.priority || 2;
          formData.deadline = newData.deadline ? new Date(newData.deadline + 'T00:00:00') : null;
          formData.assignee_id = newData.assignee?.id || null;
      } else {
          formData.title = '';
          formData.description = '';
          formData.status = 'TODO';
          formData.priority = 2;
          formData.deadline = null;
          formData.assignee_id = null;

      }
  }, { immediate: true, deep: true });
  
  onMounted(() => {
      loadUsers();
  });
  </script>
  
  <style lang="scss">
  .dp-custom-input {
      border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
      border-radius: 4px;
      padding: 8px 12px;
      width: 100%;
      box-sizing: border-box;
      font-size: 1rem;
      min-height: 40px;
      line-height: normal;
      background-color: rgb(var(--v-theme-surface));
      color: rgb(var(--v-theme-on-surface));
      transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  }
  .dp-custom-input:hover {
     border-color: rgba(var(--v-border-color), var(--v-high-emphasis-opacity));
  }
  .dp-custom-input:focus, .dp-custom-input:focus-within {
      border-color: rgb(var(--v-theme-primary));
      box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2);
      outline: none;
  }
   .dp-custom-input::placeholder {
      color: rgba(var(--v-on-surface-variant), var(--v-medium-emphasis-opacity));
      opacity: 1;
  }
  .v-theme--dark .dp-custom-input {
       border-color: rgba(var(--v-border-color), var(--v-medium-emphasis-opacity));
       background-color: rgb(var(--v-theme-surface));
       color: rgb(var(--v-theme-on-surface));
  }
  .v-theme--dark .dp-custom-input:hover {
     border-color: rgba(var(--v-border-color), var(--v-high-emphasis-opacity));
  }
  .v-theme--dark .dp-custom-input::placeholder {
      color: rgba(var(--v-on-surface-variant), var(--v-medium-emphasis-opacity));
  }
  .v-theme--dark .dp-custom-input:focus, .v-theme--dark .dp-custom-input:focus-within {
      border-color: rgb(var(--v-theme-primary));
      box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2);
  }
  </style>