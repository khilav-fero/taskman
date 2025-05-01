<template>
    <v-container fluid class="pa-4 task-list-view-container d-flex flex-column">

      <div class="d-flex justify-space-between align-center mb-4">
        <h1 class="text-h5">Your Tasks</h1>
        <v-text-field
          v-model="search"
          label="Search Tasks"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          hide-details
          clearable
          style="max-width: 300px;"
        ></v-text-field>
      </div>

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
            {{ item.deadline ? new Date(item.deadline).toLocaleDateString() : '–' }}
          </template>

          <template v-slot:item.created_at="{ item }">
            {{ item.created_at ? new Date(item.created_at).toLocaleString() : '–' }}
          </template>

           <template v-slot:item.title="{ item }">
             <div class="text-wrap">{{ item.title }}</div>
           </template>

           <template v-slot:loading>
             <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
           </template>

           <template v-slot:no-data>
              <div class="text-center pa-4">
                  No tasks found matching your search "{{ search }}".
              </div>
           </template>

        </v-data-table>

        <div
          v-else-if="showEmptyState"
          class="empty-state-content flex-grow-1 d-flex flex-column justify-center align-center text-center pa-8"
        >
          <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-view-list-outline</v-icon>
          <p class="text-h6 font-weight-regular text-medium-emphasis">No tasks found.</p>
          <p class="text-body-2 text-disabled">There are currently no tasks assigned to you.</p>
        </div>

         <div
          v-else-if="!tasksStore.getTasksLoading && !showError"
          class="initializing-placeholder flex-grow-1 d-flex justify-center align-center pa-8"
        >
           <v-progress-circular indeterminate color="primary"></v-progress-circular>
           <span class="ml-4 text-medium-emphasis">Initializing...</span>
        </div>

      </v-card>

    </v-container>
  </template>

  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useTasksStore } from '@/store/tasks';

  const tasksStore = useTasksStore();

  const componentReady = ref(false);
  const itemsPerPage = ref(15);
  const search = ref('');
  const selectedTasks = ref([]);
  const initialSortBy = ref([{ key: 'created_at', order: 'desc' }]);

  const dataTableHeaders = ref([
    { title: 'Title', key: 'title', sortable: true, class: 'text-wrap' },
    { title: 'Status', key: 'status', sortable: true, width: '150px' },
    { title: 'Priority', key: 'priority', sortable: true, width: '120px', align: 'center' },
    { title: 'Assignee', key: 'assignee.username', sortable: true, width: '160px' },
    { title: 'Creator', key: 'creator.username', sortable: true, width: '160px' },
    { title: 'Deadline', key: 'deadline', sortable: true, width: '140px' },
    { title: 'Created', key: 'created_at', sortable: true, width: '200px' },
  ]);

  const gridRowData = computed(() => tasksStore.getTasksList || []);
  const hasTasks = computed(() => gridRowData.value.length > 0);
  const showError = computed(() => !!tasksStore.getTasksError && !tasksStore.getTasksLoading);
  const showTable = computed(() =>
      componentReady.value &&
      !tasksStore.getTasksLoading &&
      !showError.value &&
      (hasTasks.value || search.value)
  );
  const showEmptyState = computed(() =>
      componentReady.value &&
      !tasksStore.getTasksLoading &&
      !showError.value &&
      !hasTasks.value &&
      !search.value
  );

  const formatPriority = (priority) => {
    const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' };
    return priorityMap[priority] || priority?.toString() || 'N/A';
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 4: return 'error';
      case 3: return 'warning';
      case 2: return 'info';
      case 1: return 'success';
      default: return 'grey';
    }
  };

  const loadTasks = async () => {
    console.log('TaskListView: Attempting to fetch tasks...');
    componentReady.value = false;
    try {
      await tasksStore.fetchTasksAction();
      console.log('TaskListView: Task fetch action complete.');
    } catch (error) {
      console.error("TaskListView: Error during fetchTasksAction:", error);
    } finally {
      componentReady.value = true;
      console.log('TaskListView: Component marked as ready.');
    }
  };

  const clearTaskError = () => {
    if (tasksStore.clearTasksError) {
      tasksStore.clearTasksError();
    } else {
      console.warn("Action 'clearTasksError' not found in tasks store.");
    }
  };

  onMounted(() => {
    console.log('TaskListView: Mounted.');
    loadTasks();
  });
  </script>

  <style lang="scss" scoped>
  .task-list-view-container {
    // Adjust based on your app bar height and container padding (e.g., pa-4 = 16px * 2)
    --app-bar-height: 64px;
    --container-padding: 32px;
    height: calc(100vh - var(--app-bar-height) - var(--container-padding));
  }

  .card-container {
    overflow: hidden;
  }

  .task-data-table {
    // Approx height for v-data-table footer with pagination etc.
    --footer-height: 58px;

    :deep(.v-table__wrapper) {
      height: calc(100% - var(--footer-height));
      overflow-y: auto;
    }

    :deep(thead th) {
      // Optional: Ensure sticky header has background matching theme surface
      // background-color: rgb(var(--v-theme-surface));
      z-index: 1;
    }

    :deep(.text-wrap) {
      white-space: normal;
      max-width: 350px; // Adjust max-width before wrapping occurs
      line-height: 1.4;
    }
  }

  .empty-state-content {
    // Styling primarily handled by utility classes in the template
  }

  .initializing-placeholder {
    // Styling primarily handled by utility classes in the template
  }
  </style>