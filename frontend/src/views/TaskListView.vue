<template>
  <v-container fluid class="pa-md-6 pa-4 task-list-view-container d-flex flex-column">
    <div class="d-flex justify-space-between align-center mb-6 flex-shrink-0 flex-wrap ga-3">
      <h1 class="text-h4 font-weight-medium header-title">TASKS</h1>
      <div class="d-flex align-center flex-wrap ga-sm-4 ga-3 task-list-actions">
        <v-text-field
          v-model="search"
          label="Search Tasks"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="comfortable"
          hide-details
          clearable
          class="search-field filter-control"
          color="primary"
          bg-color="transparent"
        ></v-text-field>
        <v-btn
          v-if="canManageTasks"
          color="primary"
          prepend-icon="mdi-plus"
          @click="openCreateDialog"
          variant="flat"
          class="create-task-btn add-user-btn"
          block-sm-and-down
        >
          Create Task
        </v-btn>
      </div>
    </div>

    <v-card
      :loading="tasksLoading"
      variant="flat"
      class="flex-grow-1 d-flex flex-column card-container"
      :color="$vuetify.theme.current.colors.surface"
      rounded="lg"
    >
      <div class="card-header-section flex-shrink-0">
        <v-alert
          v-if="showErrorAlert"
          type="error"
          variant="tonal"
          closable
          class="mx-4 my-4 flex-shrink-0"
          density="compact"
          border="start"
          elevation="2"
          prominent
          icon="mdi-alert-circle-outline"
          :title="tasksError ? 'Error Loading Tasks' : undefined"
          @update:modelValue="clearComponentError"
        >
          {{ tasksError }}
        </v-alert>
      </div>


      <div class="table-and-state-wrapper flex-grow-1 d-flex flex-column">
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
          class="flex-grow-1 task-data-table user-data-table"
          fixed-header
          height="100%"
          density="comfortable"
          hover
        >
          <template v-slot:item.priority="{ item }">
            <v-chip :color="getPriorityColor(item.priority)" size="small" label variant="tonal" class="data-table-chip">
              {{ formatPriority(item.priority) }}
            </v-chip>
          </template>
          <template v-slot:item.assignee="{ item }">
            <span class="data-table-text-secondary" :class="{'text-disabled': !item.assignee}">
                {{ item.assignee?.username || 'Unassigned' }}
            </span>
          </template>
          <template v-slot:item.creator="{ item }">
             <span class="data-table-text-secondary">
                {{ item.creator?.username || 'Unknown' }}
             </span>
          </template>
          <template v-slot:item.deadline="{ item }">
            <span class="data-table-text-secondary">
                {{ item.deadline ? new Date(item.deadline + 'T00:00:00Z').toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' }) : '–' }}
            </span>
          </template>
          <template v-slot:item.created_at="{ item }">
             <span class="data-table-text-secondary">
                {{ item.created_at ? new Date(item.created_at).toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '–' }}
             </span>
          </template>
          <template v-slot:item.title="{ item }">
            <div class="text-subtitle-1 font-weight-medium data-table-text-primary task-title-cell">{{ item.title }}</div>
            <div v-if="item.description" class="text-caption data-table-text-secondary task-description-cell">
              {{ item.description }}
            </div>
          </template>
          <template v-slot:item.status="{item}">
             <v-chip :color="getStatusColor(item.status)" size="small" label variant="flat" class="data-table-chip status-chip text-uppercase">
                {{ item.status.replace('_', ' ') }}
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
                    class="mx-1"
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
            <v-skeleton-loader type="table-row@10" :color="$vuetify.theme.current.colors.background"></v-skeleton-loader>
          </template>
          <template v-slot:no-data>
            <div class="state-content-message">
              <v-icon size="56" class="mb-3" color="grey-lighten-1">mdi-text-box-search-outline</v-icon>
              <div class="text-subtitle-1 font-weight-medium">
                <template v-if="search">No tasks found matching "{{ search }}".</template>
                <template v-else>No tasks available.</template>
              </div>
               <p class="text-body-2 text-medium-emphasis mt-1" v-if="!search && canManageTasks">Try creating a new task to get started!</p>
            </div>
          </template>
        </v-data-table>

        <div
          v-else-if="showEmptyState"
          class="state-content-message"
        >
          <v-icon size="64" :color="$vuetify.theme.current.colors.primary" class="mb-4">mdi-view-list-outline</v-icon>
          <p class="text-h6 font-weight-regular">No Tasks Yet</p>
          <p class="text-body-2 text-medium-emphasis mt-1">Create your first task to get started.</p>
           <v-btn v-if="canManageTasks" color="primary" @click="openCreateDialog" class="mt-6 add-user-btn" variant="flat">Create New Task</v-btn>
        </div>
        <div
          v-else-if="!tasksLoading && !showErrorAlert"
          class="state-content-message"
        >
          <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
          <p class="text-body-1 text-medium-emphasis mt-4">Initializing Task List...</p>
        </div>
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
      <v-card :color="$vuetify.theme.current.colors.surface" rounded="lg">
          <v-card-title class="text-h5 font-weight-medium d-flex align-center dialog-title-error">
              <v-icon start class="dialog-title-icon">mdi-alert-circle-outline</v-icon>
              Confirm Deletion
          </v-card-title>
          <v-card-text class="py-4 dialog-text-primary">
              Are you sure you want to permanently delete the task:
              <br/>
              <strong class="text-subtitle-1 my-1 d-block">{{ taskToDeleteTitle }}</strong>
              This action cannot be undone.
          </v-card-text>
          <v-card-actions class="pa-4 dialog-actions">
              <v-spacer></v-spacer>
              <v-btn
                  text
                  @click="isConfirmDeleteDialogOpen = false"
                  :disabled="formSubmitting"
                  class="dialog-btn-cancel"
              >Cancel</v-btn>
              <v-btn
                  color="error"
                  variant="flat"
                  @click="confirmDeleteTask"
                  :loading="formSubmitting"
                  class="font-weight-bold dialog-btn-confirm"
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
    case 3: return 'orange-darken-2';
    case 2: return 'info';
    case 1: return 'success-lighten-1';
    default: return 'grey';
  }
};
const getStatusColor = (status) => {
  const lowerStatus = status?.toLowerCase().replace('_', ' ');
  if (lowerStatus === 'done' || lowerStatus === 'completed') return 'success';
  if (lowerStatus === 'in progress') return 'primary';
  if (lowerStatus === 'todo' || lowerStatus === 'to do') return 'info';
  if (lowerStatus === 'blocked' || lowerStatus === 'on hold') return 'warning';
  return 'blue-grey-lighten-1';
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
    if (!componentReady.value) {
      componentReady.value = true;
    }
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
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-title {
  color: rgb(var(--v-theme-on-background));
}

.task-list-actions {
  flex-grow: 1;
  justify-content: flex-end;
}

.search-field {
  max-width: 320px;
  flex-grow: 1;
}

.card-container {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  min-height: 0;
  overflow: hidden;
}

.card-header-section {
  flex-shrink: 0;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.add-user-btn { /* Reusing class name for consistency */
  color: rgb(var(--v-theme-on-primary));
  font-weight: 500;
}
@media (max-width: 600px) {
  .task-list-actions {
    width: 100%;
    .search-field {
      max-width: none;
    }
  }
  .add-user-btn {
    width: 100%;
  }
}


.filter-control { /* Reusing class from UserListView for consistency */
  :deep(.v-field) {
    background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
    border-radius: var(--v-border-radius-lg);
    transition: box-shadow 0.2s ease-in-out, border-color 0.2s ease-in-out;
  }
  :deep(.v-field__outline) {
    border-color: rgba(var(--v-theme-on-surface), 0.15) !important;
  }
  &:hover :deep(.v-field__outline) {
    border-color: rgba(var(--v-theme-on-surface), 0.35) !important;
  }
  &.v-input--is-focused :deep(.v-field__outline) {
    border-color: rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12);
  }
  :deep(.v-label.v-field-label) {
    color: rgba(var(--v-theme-on-surface), 0.65) !important;
    font-weight: 400;
  }
  :deep(.v-field--active .v-label.v-field-label) {
    color: rgb(var(--v-theme-primary)) !important;
  }
  :deep(input) {
    color: rgb(var(--v-theme-on-surface)) !important;
  }
  :deep(.v-field__prepend-inner .v-icon) {
    color: rgba(var(--v-theme-on-surface), 0.5) !important;
  }
}

.table-and-state-wrapper {
  overflow: hidden;
  position: relative;
  flex-grow: 1;
}

.user-data-table { /* Reusing class name for consistency in table styling */
  color: rgb(var(--v-theme-on-surface));
  border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);

  :deep(.v-table__wrapper) {
    overflow-y: auto;
    height: 100%;
    border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);
  }

  :deep(thead th) {
    position: sticky;
    top: 0;
    background-color: rgba(var(--v-theme-surface-rgb), 0.98) !important;
    backdrop-filter: blur(6px);
    z-index: 10;
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.1) !important;
    color: rgba(var(--v-theme-on-surface), 0.75) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem; 
    text-transform: uppercase;
    letter-spacing: 0.04em;
    height: 48px !important;
  }

  :deep(tbody tr:hover) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.05) !important;
  }
  :deep(tbody tr.v-data-table__tr--selected:hover) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.08) !important;
  }
  :deep(tbody tr.v-data-table__tr--selected td) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.04) !important;
  }


  :deep(.v-data-table__td) {
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08) !important;
    padding: 10px 16px !important;
    font-size: 0.875rem; 
    height: auto !important; // Allow cells to grow for title/description
    vertical-align: top; // Align content to top for multi-line cells
  }
  :deep(.v-data-table__td.v-data-table-column--select) { // Center checkbox vertically
      vertical-align: middle;
  }
   :deep(.v-data-table__td > .v-data-table-column__checkbox) { // Ensure checkbox doesn't add extra height
        height: auto;
   }


  .data-table-text-primary {
    color: rgb(var(--v-theme-on-surface));
    line-height: 1.45;
    font-weight: 500;
  }

  .data-table-text-secondary {
    color: rgba(var(--v-theme-on-surface), 0.7);
    line-height: 1.45;
    font-size: 0.8125rem;
  }

  .task-title-cell {
    display: block;
    white-space: normal;
    word-break: break-word;
  }
  .task-description-cell {
    font-size: 0.8125rem;
    margin-top: 4px;
    max-height: 3.6em; /* Approx 2-3 lines */
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    white-space: normal;
  }


  .data-table-chip {
    font-weight: 500 !important;
    font-size: 0.75rem !important; 
    padding: 2px 8px;
    height: 24px !important;
    letter-spacing: 0.02em;
    &.status-chip {
      color: rgb(var(--v-theme-on-primary)) !important; // Assuming flat variant has on-primary text
    }
  }

  .action-icons .v-btn {
    color: rgba(var(--v-theme-on-surface), 0.6);
    &:hover {
      color: rgb(var(--v-theme-primary));
    }
    &[color="error"]:hover {
      color: rgb(var(--v-theme-error));
    }
  }

  :deep(.v-data-table-footer) {
    border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
    padding: 8px 0;
    background-color: rgb(var(--v-theme-surface));
    border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);
  }
}

.state-content-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 40px 24px;
  flex-grow: 1;
  color: rgb(var(--v-theme-on-surface));
}
.state-content-message .text-h6,
.state-content-message .text-subtitle-1 {
   color: rgba(var(--v-theme-on-surface), 0.9);
}
.state-content-message .text-body-1,
.state-content-message .text-body-2 {
   color: rgba(var(--v-theme-on-surface), 0.65);
}

/* Dialog Styles (copied from UserListView for consistency) */
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
}
.dialog-btn-cancel {
  color: rgba(var(--v-theme-on-surface), 0.75);
  &:hover {
    color: rgb(var(--v-theme-on-surface));
  }
}
.dialog-btn-confirm {
  color: rgb(var(--v-theme-on-error)) !important; // For flat error button text
}

</style>