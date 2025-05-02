<template>
    <v-container fluid class="pa-4 task-list-view-container d-flex flex-column">
      <div class="d-flex justify-space-between align-center mb-4 flex-shrink-0">
        <h1 class="text-h5">Your Tasks</h1>
        <div class="d-flex align-center">
          <v-text-field
            v-model="search"
            label="Search Tasks"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            class="mr-2"
            style="max-width: 300px;"
          ></v-text-field>
          <v-btn
            v-if="canManageTasks"
            color="primary"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
            variant="elevated"
            class="ml-2"
          >
            Create Task
          </v-btn>
        </div>
      </div>
  
      <!-- Loading/Error Section -->
      <v-card
        :loading="tasksStore.getTasksLoading"
        variant="outlined"
        class="flex-grow-1 d-flex flex-column card-container"
      >
        <v-alert
          v-if="showError"
          type="error"
          variant="tonal"
          closable
          class="ma-2 flex-shrink-0"
          density="compact"
          title="Error Loading Tasks"
          @update:modelValue="clearTaskError"
        >
          {{ tasksStore.getTasksError }}
        </v-alert>
  
        <!-- Vuetify Data Table -->
        <v-data-table
          v-if="showTable"
          v-model="selectedTasks"
          :headers="dataTableHeaders"
          :items="gridRowData"
          :search="search"
          :loading="tasksStore.getTasksLoading"
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
            <v-chip :color="getPriorityColor(item.priority)" size="small" label variant="tonal">
              {{ formatPriority(item.priority) }}
            </v-chip>
          </template>
          <template v-slot:item.assignee="{ item }">
            {{ item.assignee?.username || 'Unassigned' }}
          </template>
          <template v-slot:item.creator="{ item }">
            {{ item.creator?.username || 'Unknown' }}
          </template>
          <template v-slot:item.deadline="{ item }">
            {{ item.deadline ? new Date(item.deadline + 'T00:00:00').toLocaleDateString() : '–' }}
          </template>
          <template v-slot:item.created_at="{ item }">
            {{ item.created_at ? new Date(item.created_at).toLocaleString() : '–' }}
          </template>
          <template v-slot:item.title="{ item }">
            <div class="text-wrap font-weight-medium">{{ item.title }}</div>
            <div v-if="item.description" class="text-caption text-medium-emphasis text-wrap">
              {{ item.description }}
            </div>
          </template>
          <template v-slot:item.actions="{ item }">
            <div>
              <v-tooltip text="Edit Task" location="top">
                <template v-slot:activator="{ props: tooltip }">
                  <v-icon
                    v-bind="tooltip"
                    v-if="canManageTasks"
                    small
                    icon="mdi-pencil"
                    class="mr-2"
                    @click.stop="openEditDialog(item)"
                    color="primary"
                    :aria-label="'Edit task ' + item.title"
                  ></v-icon>
                </template>
              </v-tooltip>
              <v-tooltip text="Delete Task" location="top">
                <template v-slot:activator="{ props: tooltip }">
                  <v-icon
                    v-bind="tooltip"
                    v-if="canManageTasks"
                    small
                    icon="mdi-delete"
                    @click.stop="openDeleteDialog(item.id)"
                    color="error"
                    :aria-label="'Delete task ' + item.title"
                  ></v-icon>
                </template>
              </v-tooltip>
            </div>
          </template>
          <template v-slot:loading>
            <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
          </template>
          <template v-slot:no-data>
            <div class="text-center pa-4 text-medium-emphasis">
              <template v-if="search">No tasks found matching your search "{{ search }}".</template>
              <template v-else>No tasks available.</template>
            </div>
          </template>
        </v-data-table>
  
        <!-- Empty/Initializing States -->
        <div
          v-else-if="showEmptyState"
          class="empty-state-content flex-grow-1 d-flex flex-column justify-center align-center text-center pa-8"
        >
          <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-view-list-outline</v-icon>
          <p class="text-h6 font-weight-regular text-medium-emphasis">No tasks found.</p>
          <p class="text-body-2 text-disabled">There are currently no tasks matching your criteria.</p>
        </div>
        <div
          v-else-if="!tasksStore.getTasksLoading && !showError"
          class="initializing-placeholder flex-grow-1 d-flex justify-center align-center pa-8"
        >
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <span class="ml-4 text-medium-emphasis">Initializing...</span>
        </div>
      </v-card>
  
      <!-- Task Form Dialog -->
      <v-dialog v-model="isFormDialogOpen" persistent max-width="700px" @keydown.esc="closeFormDialog">
        <TaskForm
          :initial-data="editingTask"
          :loading="tasksStore.isSubmitting"
          :error="tasksStore.getFormError"
          @submit="onFormSubmit"
          @cancel="closeFormDialog"
        />
      </v-dialog>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useTasksStore } from '@/store/tasks';
  import { useAuthStore } from '@/store/auth';
  import TaskForm from '@/components/TaskForm.vue';
  
  const tasksStore = useTasksStore();
  const authStore = useAuthStore();
  
  const componentReady = ref(false);
  const itemsPerPage = ref(15);
  const search = ref('');
  const selectedTasks = ref([]);
  const initialSortBy = ref([{ key: 'created_at', order: 'desc' }]);
  
  const dataTableHeaders = ref([
    { title: 'Title', key: 'title', sortable: true, class: 'text-wrap', minWidth: '300px' },
    { title: 'Status', key: 'status', sortable: true, width: '150px' },
    { title: 'Priority', key: 'priority', sortable: true, width: '120px', align: 'center' },
    { title: 'Assignee', key: 'assignee', sortable: true, sortKey: 'assignee.username', width: '160px' },
    { title: 'Creator', key: 'creator', sortable: true, sortKey: 'creator.username', width: '160px' },
    { title: 'Deadline', key: 'deadline', sortable: true, width: '140px' },
    { title: 'Created', key: 'created_at', sortable: true, width: '200px' },
    { title: 'Actions', key: 'data-table-actions', sortable: false, align: 'center', width: '120px' }
  ]);
  
  const gridRowData = computed(() => tasksStore.getTasksList || []);
  const hasTasks = computed(() => gridRowData.value.length > 0);
  const showError = computed(() => !!tasksStore.getTasksError && !tasksStore.getTasksLoading);
  const showTable = computed(() =>
    componentReady.value && !tasksStore.getTasksLoading && !showError.value && (hasTasks.value || search.value)
  );
  const showEmptyState = computed(() =>
    componentReady.value && !tasksStore.getTasksLoading && !showError.value && !hasTasks.value && !search.value
  );
  const canManageTasks = computed(() => {
    const role = authStore.userRole;
    return role === 'ADMIN' || role === 'MANAGER';
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
      case 1: return 'success';
      default: return 'grey';
    }
  };
  
  const openCreateDialog = () => {
    editingTask.value = null;
    tasksStore.clearFormError();
    isFormDialogOpen.value = true;
  };
  const openEditDialog = (taskData) => {
    editingTask.value = { ...taskData };
    tasksStore.clearFormError();
    isFormDialogOpen.value = true;
  };
  const closeFormDialog = () => {
    isFormDialogOpen.value = false;
    editingTask.value = null;
    tasksStore.clearFormError();
  };
  const openDeleteDialog = (taskId) => {
    if (confirm(`Are you sure you want to delete task ID: ${taskId}?`)) {
      // await tasksStore.deleteTaskAction(taskId); // Uncomment and implement as needed
      // await loadTasks(); // Uncomment if needed to reload after delete
    }
  };
  
  const onFormSubmit = async (formDataFromForm) => {
    let success = false;
    try {
      if (editingTask.value && editingTask.value.id) {
        await tasksStore.updateTaskAction(editingTask.value.id, formDataFromForm);
      } else {
        await tasksStore.createTaskAction(formDataFromForm);
      }
      success = true;
      await loadTasks();
    } catch (error) {
      success = false;
    }
    if (success) {
      closeFormDialog();
    }
  };
  
  const loadTasks = async () => {
    componentReady.value = false;
    try {
      await tasksStore.fetchTasksAction();
    } finally {
      componentReady.value = true;
    }
  };
  
  const clearTaskError = () => {
    if (tasksStore.clearTasksError) {
      tasksStore.clearTasksError();
    }
  };
  
  onMounted(() => {
    loadTasks();
  });
  </script>
  
  <style lang="scss" scoped>
  .task-list-view-container {
    --app-bar-height: 64px;
    --container-padding: 32px;
    height: calc(100vh - var(--app-bar-height) - var(--container-padding));
  }
  
  .card-container {
    overflow: hidden;
  }
  
  .task-data-table {
    --footer-height: 58px;
    :deep(.v-table__wrapper) {
      height: calc(100% - var(--footer-height));
      overflow-y: auto;
    }
    :deep(thead th) {
      position: sticky;
      top: 0;
      background-color: rgb(var(--v-theme-surface));
      z-index: 1;
    }
    :deep(.text-wrap) {
      white-space: normal;
      word-break: break-word;
      max-width: 350px;
      line-height: 1.4;
    }
  }
  .empty-state-content, .initializing-placeholder {
    /* Utility classes handle most styling */
  }
  </style>
  