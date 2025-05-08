<template>
  <v-container fluid class="pa-4 task-list-view-container d-flex flex-column">
    <div class="d-flex justify-space-between align-center mb-5 flex-shrink-0 flex-wrap ga-2">
      <h1 class="text-h5 font-weight-medium header-title">TASKS</h1>
      <div class="d-flex align-center flex-wrap ga-2">
        <v-text-field
          v-model="search"
          label="Search Tasks"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          hide-details
          clearable
          class="search-field"
          style="min-width: 250px; max-width: 350px;"
          color="primary"
        ></v-text-field>
        <v-btn
          v-if="canManageTasks"
          color="primary"
          prepend-icon="mdi-plus"
          @click="openCreateDialog"
          variant="flat"
          class="create-task-btn"
        >
          Create Task
        </v-btn>
      </div>
    </div>

    <v-card
      :loading="tasksLoading"
      variant="outlined"
      class="flex-grow-1 d-flex flex-column card-container"
      :color="$vuetify.theme.current.colors.surface"
    >
      <v-alert
        v-if="showErrorAlert"
        type="error"
        variant="tonal"
        closable
        class="ma-2 flex-shrink-0"
        density="compact"
        title="Error Loading Tasks"
        @update:modelValue="clearComponentError"
      >
        {{ tasksError }}
      </v-alert>

      <v-data-table
        v-if="showTable"
        v-model="selectedTasks"
        :headers="dataTableHeaders"
        :items="tasksList"
        :search="search"
        :loading="tasksLoading"
        :items-per-page="itemsPerPage"
        :sort-by="initialSortBy"
        item-value="id"
        show-select
        class="flex-grow-1 task-data-table"
        fixed-header
        height="100%"
        density="comfortable"
        hover
      >
        <template v-slot:item.priority="{ item }">
          <v-chip :color="getPriorityColor(item.priority)" size="small" label variant="tonal" class="font-weight-medium data-table-chip">
            {{ formatPriority(item.priority) }}
          </v-chip>
        </template>
        <template v-slot:item.assignee="{ item }">
          <span class="data-table-secondary-text" :class="{'text-disabled': !item.assignee}">
              {{ item.assignee?.username || 'Unassigned' }}
          </span>
        </template>
        <template v-slot:item.creator="{ item }">
           <span class="data-table-secondary-text">
              {{ item.creator?.username || 'Unknown' }}
           </span>
        </template>
        <template v-slot:item.deadline="{ item }">
          <span class="data-table-secondary-text">
              {{ item.deadline ? new Date(item.deadline + 'T00:00:00Z').toLocaleDateString() : '–' }}
          </span>
        </template>
        <template v-slot:item.created_at="{ item }">
           <span class="data-table-secondary-text">
              {{ item.created_at ? new Date(item.created_at).toLocaleString() : '–' }}
           </span>
        </template>
        <template v-slot:item.title="{ item }">
          <div class="text-subtitle-1 font-weight-medium cell-title data-table-primary-text">{{ item.title }}</div>
          <div v-if="item.description" class="text-caption cell-description data-table-description-text">
            {{ item.description }}
          </div>
        </template>
        <template v-slot:item.status="{item}">
           <v-chip :color="getStatusColor(item.status)" size="small" label variant="flat" class="font-weight-bold text-uppercase data-table-chip status-chip">
              {{ item.status }}
           </v-chip>
        </template>
        <template v-slot:item.actions="{ item }">
          <div class="action-icons">
            <v-tooltip text="Edit Task" location="top">
              <template v-slot:activator="{ props: tooltip }">
                <v-btn
                  v-bind="tooltip"
                  v-if="canManageTasks"
                  icon="mdi-pencil-outline"
                  variant="text"
                  size="small"
                  @click.stop="openEditDialog(item)"
                  color="primary"
                  class="mr-1"
                  :aria-label="'Edit task ' + item.title"
                ></v-btn>
              </template>
            </v-tooltip>
            <v-tooltip text="Delete Task" location="top">
              <template v-slot:activator="{ props: tooltip }">
                <v-btn
                  v-bind="tooltip"
                  v-if="canManageTasks"
                  icon="mdi-delete-outline"
                  variant="text"
                  size="small"
                  @click.stop="openDeleteDialog(item)"
                  color="error"
                  :aria-label="'Delete task ' + item.title"
                ></v-btn>
              </template>
            </v-tooltip>
          </div>
        </template>
        <template v-slot:loading>
          <v-skeleton-loader type="table-row@10" :color="$vuetify.theme.current.colors.surface"></v-skeleton-loader>
        </template>
        <template v-slot:no-data>
          <div class="text-center pa-6 text-medium-emphasis">
            <v-icon size="48" class="mb-3" color="grey-lighten-1">mdi-text-box-search-outline</v-icon>
            <div class="text-subtitle-1 data-table-primary-text">
              <template v-if="search">No tasks found matching "{{ search }}".</template>
              <template v-else>No tasks available.</template>
            </div>
             <p class="text-caption data-table-secondary-text" v-if="!search && canManageTasks">Try creating a new task to get started!</p>
          </div>
        </template>
      </v-data-table>

      <div
        v-else-if="showEmptyState"
        class="empty-state-content"
      >
        <v-icon size="64" :color="$vuetify.theme.current.colors.secondary" class="mb-4">mdi-view-list-outline</v-icon>
        <p class="text-h6 font-weight-regular data-table-primary-text">No Tasks Yet</p>
        <p class="text-body-2 data-table-secondary-text">Create your first task to get started.</p>
         <v-btn v-if="canManageTasks" color="primary" @click="openCreateDialog" class="mt-4 create-task-btn">Create New Task</v-btn>
      </div>
      <div
        v-else-if="!tasksLoading && !showErrorAlert"
        class="initializing-placeholder"
      >
        <v-progress-circular indeterminate color="primary" size="40"></v-progress-circular>
        <span class="ml-3 data-table-secondary-text">Initializing Task List...</span>
      </div>
    </v-card>

    <v-dialog v-model="isFormDialogOpen" persistent max-width="700px" @keydown.esc="closeFormDialog">
      <TaskForm
        :initial-data="editingTask"
        :loading="formSubmitting"
        :error="formError"
        @submit="onFormSubmit"
        @cancel="closeFormDialog"
        @clear-form-error="clearFormError"
        key="task-form-component"
      />
    </v-dialog>

    <v-dialog v-model="isConfirmDeleteDialogOpen" persistent max-width="450px">
      <v-card :color="$vuetify.theme.current.colors.surface">
          <v-card-title class="text-h5 font-weight-medium d-flex align-center" :style="{ color: $vuetify.theme.current.colors.error }">
              <v-icon start :color="$vuetify.theme.current.colors.error">mdi-alert-circle-outline</v-icon>
              Confirm Deletion
          </v-card-title>
          <v-card-text class="py-4 data-table-primary-text">
              Are you sure you want to permanently delete the task:
              <br>
              <strong class="text-subtitle-1 my-1 d-block">{{ taskToDeleteTitle }}</strong>
              This action cannot be undone.
          </v-card-text>
          <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                  text
                  @click="isConfirmDeleteDialogOpen = false"
                  :disabled="formSubmitting"
                  class="data-table-secondary-text"
              >Cancel</v-btn>
              <v-btn
                  color="error"
                  variant="flat"
                  @click="confirmDeleteTask"
                  :loading="formSubmitting"
                  class="font-weight-bold"
              >Delete Task</v-btn>
          </v-card-actions>
      </v-card>
  </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, inject } from 'vue';
import { fetchTasks, createTask as createTaskApi, updateTask as updateTaskApi, deleteTaskApi as deleteTaskServiceApi } from '@/services/taskService';
import TaskForm from '@/components/TaskForm.vue';

const currentUser = inject('currentUser', ref(null));

const componentReady = ref(false);
const itemsPerPage = ref(15);
const search = ref('');
const selectedTasks = ref([]);
const initialSortBy = ref([{ key: 'created_at', order: 'desc' }]);

const tasksList = ref([]);
const tasksLoading = ref(false);
const tasksError = ref(null);
const formSubmitting = ref(false);
const formError = ref(null);

const isConfirmDeleteDialogOpen = ref(false);
const taskToDelete = ref(null);
const taskToDeleteTitle = computed(() => taskToDelete.value?.title || 'this task');

const dataTableHeaders = ref([
  { title: 'Title & Description', key: 'title', sortable: true, class: 'text-wrap', minWidth: '300px', width: '35%' },
  { title: 'Status', key: 'status', sortable: true, width: '130px', align: 'center' },
  { title: 'Priority', key: 'priority', sortable: true, width: '120px', align: 'center' },
  { title: 'Assignee', key: 'assignee', sortable: true, value: item => item.assignee?.username, width: '160px' },
  { title: 'Creator', key: 'creator', sortable: true, value: item => item.creator?.username, width: '160px' },
  { title: 'Deadline', key: 'deadline', sortable: true, width: '140px' },
  { title: 'Created', key: 'created_at', sortable: true, width: '180px' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '120px' }
]);

const hasTasks = computed(() => tasksList.value.length > 0);
const showErrorAlert = computed(() => !!tasksError.value && !tasksLoading.value);

const showTable = computed(() =>
  componentReady.value && !tasksLoading.value && !showErrorAlert.value && (hasTasks.value || !!search.value)
);
const showEmptyState = computed(() =>
  componentReady.value && !tasksLoading.value && !showErrorAlert.value && !hasTasks.value && !search.value
);

const userRole = computed(() => currentUser.value?.profile?.role || null);
const canManageTasks = computed(() => {
  return userRole.value === 'ADMIN' || userRole.value === 'MANAGER';
});

const isFormDialogOpen = ref(false);
const editingTask = ref(null);

const formatPriority = (priority) => {
  return { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' }[priority] || priority?.toString() || 'N/A';
};
const getPriorityColor = (priority) => {
  switch (priority) {
    case 4: return 'error';
    case 3: return 'warning';
    case 2: return 'info';
    case 1: return 'success';
    default: return 'secondary';
  }
};
const getStatusColor = (status) => {
  const lowerStatus = status?.toLowerCase();
  if (lowerStatus === 'done' || lowerStatus === 'completed') return 'success';
  if (lowerStatus === 'in_progress' || lowerStatus === 'in progress') return 'info';
  if (lowerStatus === 'blocked' || lowerStatus === 'on_hold') return 'warning';
  return 'secondary';
};

const openCreateDialog = () => {
  editingTask.value = null;
  formError.value = null;
  isFormDialogOpen.value = true;
};
const openEditDialog = (taskData) => {
  editingTask.value = { ...taskData };
  formError.value = null;
  isFormDialogOpen.value = true;
};
const closeFormDialog = () => {
  isFormDialogOpen.value = false;
  editingTask.value = null;
  formError.value = null;
};

const openDeleteDialog = (task) => {
  taskToDelete.value = task;
  isConfirmDeleteDialogOpen.value = true;
};

const confirmDeleteTask = async () => {
  if (!taskToDelete.value || !taskToDelete.value.id) return;
  formSubmitting.value = true;
  formError.value = null;
  try {
    await deleteTaskServiceApi(taskToDelete.value.id);
    await loadTasks();
    isConfirmDeleteDialogOpen.value = false;
    taskToDelete.value = null;
  } catch (err) {
    formError.value = err?.detail || err?.message || 'Failed to delete task.';
    console.error("Error deleting task:", err);
  } finally {
    formSubmitting.value = false;
  }
};

const onFormSubmit = async (formDataFromForm) => {
  formSubmitting.value = true;
  formError.value = null;
  let success = false;
  try {
    if (editingTask.value && editingTask.value.id) {
      await updateTaskApi(editingTask.value.id, formDataFromForm);
    } else {
      await createTaskApi(formDataFromForm);
    }
    success = true;
  } catch (err) {
    formError.value = err?.detail || err?.message || (editingTask.value ? 'Failed to update task.' : 'Failed to create task.');
    console.error("Error submitting task form:", err);
  } finally {
    formSubmitting.value = false;
  }

  if (success) {
    await loadTasks();
    closeFormDialog();
  }
};

const loadTasks = async () => {
  tasksLoading.value = true;
  tasksError.value = null;
  try {
    const responseData = await fetchTasks();
     if (responseData && typeof responseData === 'object' && Array.isArray(responseData.results)) {
        tasksList.value = responseData.results;
    } else if (Array.isArray(responseData)) {
        tasksList.value = responseData;
    } else {
        tasksList.value = [];
        console.warn("Received task data in unexpected format:", responseData);
    }
  } catch (err) {
     tasksError.value = err?.detail || err?.message || 'Could not load tasks.';
     console.error('TaskListView: Could not load tasks.', err);
     tasksList.value = [];
  }
  finally {
    tasksLoading.value = false;
    componentReady.value = true;
  }
};

const clearComponentError = () => {
  tasksError.value = null;
};
const clearFormError = () => {
  formError.value = null;
};

onMounted(() => {
  componentReady.value = false;
  loadTasks();
});
</script>

<style lang="scss" scoped>
.task-list-view-container {
  height: calc(100vh - 64px);
  padding-bottom: 16px;
}
.card-container {
  border: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.12);
}
.header-title {
  color: rgb(var(--v-theme-on-background));
}
.search-field .v-field__input {
    min-height: 40px;
}
.create-task-btn {
  color: rgb(var(--v-theme-on-primary));
}
.task-data-table {
  --footer-height: 58px;
  color: rgb(var(--v-theme-on-surface));
  :deep(.v-table__wrapper) {
    height: calc(100% - var(--footer-height));
    overflow-y: auto;
  }
  :deep(thead th) {
    position: sticky;
    top: 0;
    background-color: rgba(var(--v-theme-surface-rgb), 0.97) !important;
    backdrop-filter: blur(4px);
    z-index: 10;
    border-bottom: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.15) !important;
    color: rgba(var(--v-theme-on-surface-rgb), 0.8) !important;
    font-weight: 500 !important;
  }
  :deep(tbody tr) {
      &:hover {
          background-color: rgba(var(--v-theme-primary-rgb), 0.07) !important;
      }
      &.v-data-table__tr--selected:hover {
          background-color: rgba(var(--v-theme-primary-rgb), 0.12) !important;
      }
  }
  :deep(.v-data-table__td) {
      border-bottom: thin solid rgba(var(--v-theme-on-surface-rgb), 0.08) !important;
      padding-top: 12px !important;
      padding-bottom: 12px !important;
  }
   :deep(.v-data-table-footer) {
      border-top: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.15) !important;
      color: rgba(var(--v-theme-on-surface-rgb), 0.7) !important;
  }
  .data-table-primary-text, .cell-title {
      color: rgb(var(--v-theme-on-surface));
      line-height: 1.45;
  }
  .data-table-secondary-text, .cell-description {
      color: rgba(var(--v-theme-on-surface-rgb), 0.75);
      line-height: 1.45;
  }
  .data-table-description-text {
      font-size: 0.8rem;
      margin-top: 2px;
      max-height: 3.9em;
      overflow: hidden;
      text-overflow: ellipsis;
  }
  .data-table-chip {
      &.status-chip {
          color: rgb(var(--v-theme-on-primary)) !important;
      }
  }
  .action-icons .v-btn {
      color: rgba(var(--v-theme-on-surface-rgb), 0.65);
      &:hover {
          color: rgb(var(--v-theme-primary));
      }
  }
  .action-icons .v-btn[color="error"] {
     &:hover {
       color: rgb(var(--v-theme-error)) !important;
     }
  }
}
.empty-state-content, .initializing-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 32px;
  flex-grow: 1;
  color: rgb(var(--v-theme-on-surface));
}
.empty-state-content .text-h6, .empty-state-content .text-body-2 {
   color: rgba(var(--v-theme-on-surface-rgb), 0.8);
}
.initializing-placeholder .text-medium-emphasis {
   color: rgba(var(--v-theme-on-surface-rgb), 0.7);
}
</style>