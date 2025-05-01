<template>
    <v-container fluid class="pa-4 task-list-view-container d-flex flex-column">
  
      <!-- Header -->
      <div class="d-flex justify-space-between align-center mb-4">
        <h1 class="text-h5">My Tasks</h1>
        <!-- Add optional search field -->
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
        <!-- Add optional action buttons here if needed -->
        <!-- <v-btn color="primary">New Task</v-btn> -->
      </div>
  
      <!-- Main Content Card -->
      <v-card
        :loading="tasksStore.getTasksLoading"
        variant="outlined"
        class="flex-grow-1 d-flex flex-column"
      >
        <!-- Error Alert -->
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
          class="flex-grow-1 data-table-dense"
          fixed-header
          height="100%" 
          density="comfortable"
        >
          <!-- Custom Slot for Priority -->
          <template v-slot:item.priority="{ item }">
            <v-chip :color="getPriorityColor(item.priority)" size="small" label variant="tonal">
              {{ formatPriority(item.priority) }}
            </v-chip>
          </template>
  
          <!-- Custom Slot for Assignee -->
          <template v-slot:item.assignee="{ item }">
            {{ item.assignee?.username || 'Unassigned' }}
          </template>
  
          <!-- Custom Slot for Creator -->
           <template v-slot:item.creator="{ item }">
            {{ item.creator?.username || 'Unknown' }}
          </template>
  
          <!-- Custom Slot for Deadline -->
          <template v-slot:item.deadline="{ item }">
            {{ item.deadline ? new Date(item.deadline).toLocaleDateString() : '–' }}
          </template>
  
          <!-- Custom Slot for Created At -->
          <template v-slot:item.created_at="{ item }">
            {{ item.created_at ? new Date(item.created_at).toLocaleString() : '–' }}
          </template>
  
          <!-- Custom Slot for Title (if wrapping is needed) -->
           <template v-slot:item.title="{ item }">
             <div class="text-wrap">{{ item.title }}</div>
           </template>
  
           <!-- Loading State (alternative to card loading) -->
           <template v-slot:loading>
             <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
           </template>
  
           <!-- No Data State (when search yields no results) -->
           <template v-slot:no-data>
              <div class="text-center pa-4">
                  No tasks found matching your search "{{ search }}".
              </div>
           </template>
  
        </v-data-table>
  
        <!-- Empty State (when initial load yields no data) -->
        <div
          v-else-if="showEmptyState"
          class="empty-state-content flex-grow-1 d-flex flex-column justify-center align-center text-center pa-8"
        >
          <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-view-list-outline</v-icon>
          <p class="text-h6 font-weight-regular text-medium-emphasis">No tasks found.</p>
          <p class="text-body-2 text-disabled">There are currently no tasks assigned to you.</p>
          <!-- Optional: Add a button to create a task -->
          <!-- <v-btn color="primary" variant="tonal" class="mt-4">Create New Task</v-btn> -->
        </div>
  
        <!-- Initializing / Placeholder -->
         <div
          v-else-if="!tasksStore.getTasksLoading && !showError"
          class="initializing-placeholder flex-grow-1 d-flex justify-center align-center pa-8"
        >
          <!-- Usually covered by v-card loading, but good fallback -->
           <v-progress-circular indeterminate color="primary"></v-progress-circular>
           <span class="ml-4 text-medium-emphasis">Initializing...</span>
        </div>
  
      </v-card>
  
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useTasksStore } from '@/store/tasks';
  // No AG Grid imports needed anymore
  // VDataTable is usually auto-imported by Vuetify
  
  // --- Pinia Store ---
  const tasksStore = useTasksStore();
  
  // --- Component State ---
  const componentReady = ref(false); // Tracks if initial fetch attempt is done
  const itemsPerPage = ref(15);
  const search = ref(''); // For the search text field
  const selectedTasks = ref([]); // Holds the selected task items
  const initialSortBy = ref([{ key: 'created_at', order: 'desc' }]); // Default sort
  
  // --- Data Table Headers ---
  // Structure for v-data-table headers
  const dataTableHeaders = ref([
    // Note: Selection checkbox column is added automatically via `show-select` prop
    {
      title: 'Title', key: 'title', sortable: true,
      // width: '30%', // Example width
      class: 'text-wrap' // Apply class for potential wrapping via CSS
    },
    { title: 'Status', key: 'status', sortable: true, width: '150px' },
    {
      title: 'Priority', key: 'priority', sortable: true, width: '120px', align: 'center'
      // Custom rendering via slot: item.priority
    },
    {
      title: 'Assignee', key: 'assignee.username', sortable: true, width: '160px'
      // Custom rendering via slot: item.assignee (handles missing assignee)
    },
    {
      title: 'Creator', key: 'creator.username', sortable: true, width: '160px'
      // Custom rendering via slot: item.creator
    },
    {
      title: 'Deadline', key: 'deadline', sortable: true, width: '140px'
      // Custom rendering via slot: item.deadline
    },
    {
      title: 'Created', key: 'created_at', sortable: true, width: '200px'
      // Custom rendering via slot: item.created_at
    },
  ]);
  
  // --- Computed Properties for State ---
  const gridRowData = computed(() => tasksStore.getTasksList || []);
  const hasTasks = computed(() => gridRowData.value.length > 0);
  const showError = computed(() => !!tasksStore.getTasksError && !tasksStore.getTasksLoading);
  // Show table if ready, not loading, no error, and has data OR if searching (even if no results)
  const showTable = computed(() =>
      componentReady.value &&
      !tasksStore.getTasksLoading &&
      !showError.value &&
      (hasTasks.value || search.value) // Show table if there's data OR if user is searching
  );
  // Show empty state only if ready, not loading, no error, no data, and not searching
  const showEmptyState = computed(() =>
      componentReady.value &&
      !tasksStore.getTasksLoading &&
      !showError.value &&
      !hasTasks.value &&
      !search.value
  );
  
  // --- Helper Functions ---
  const formatPriority = (priority) => {
    const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' };
    return priorityMap[priority] || priority?.toString() || 'N/A';
  };
  
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 4: return 'error'; // Urgent
      case 3: return 'warning'; // High
      case 2: return 'info'; // Medium
      case 1: return 'success'; // Low (or 'grey' or 'primary')
      default: return 'grey';
    }
  };
  
  // --- Data Loading ---
  const loadTasks = async () => {
    console.log('TaskListView: Attempting to fetch tasks...');
    componentReady.value = false; // Reset ready state on reload
    try {
      // IMPORTANT: Ensure your fetchTasksAction fetches ALL tasks
      // if you want client-side sorting/pagination/filtering to work correctly.
      // If you intend server-side operations, you'd use v-data-table-server
      // and pass options like page, itemsPerPage, sortBy to the action.
      await tasksStore.fetchTasksAction();
      console.log('TaskListView: Task fetch action complete.');
    } catch (error) {
      console.error("TaskListView: Error during fetchTasksAction:", error);
      // Error is handled by the store's state via showError computed prop
    } finally {
      componentReady.value = true; // Mark as ready after attempt
      console.log('TaskListView: Component marked as ready.');
    }
  };
  
  // --- Error Handling ---
  const clearTaskError = () => {
    if (tasksStore.clearTasksError) {
      tasksStore.clearTasksError();
    } else {
      console.warn("Action 'clearTasksError' not found in tasks store.");
    }
  };
  
  // --- Lifecycle Hook ---
  onMounted(() => {
    console.log('TaskListView: Mounted.');
    loadTasks();
  
    // Example: Log selected tasks when they change
    // watch(selectedTasks, (newSelection) => {
    //   console.log('Selected tasks:', newSelection);
    // });
  });
  </script>
  
  <style lang="scss" scoped>
  // Main container takes full height minus header/padding etc.
  .task-list-view-container {
    height: calc(100vh - 64px - 32px); // Example: Adjust based on your app bar height and container padding
  }
  
  // Style the card containing the table/states
  .v-card {
    overflow: hidden; // Prevent potential overflows
  }
  
  // Style the data table
  .v-data-table {
    // Allows table to take full height within the card's flex container
    // The `height="100%"` prop on v-data-table is also important
    :deep(.v-table__wrapper) {
        height: calc(100% - 58px); // Adjust based on header/footer height of the table (approx 58px for footer)
        overflow-y: auto;
    }
  
    // Ensure header stays put
    :deep(thead th) {
      // background-color: rgb(var(--v-theme-surface)); // Make header sticky background match
      z-index: 1;
    }
  
    // Optional: Style for dense table look if needed
    // &.data-table-dense {
    //   :deep(td), :deep(th) {
    //     padding: 0 8px !important; // Reduce padding
    //   }
    //   :deep(.v-data-table-header__content) {
    //      justify-content: flex-start; // Align header text left
    //   }
    // }
  
      // Class to allow text wrapping in specific columns if needed
      :deep(.text-wrap) {
          white-space: normal;
          max-width: 350px; // Example max-width before wrapping
          line-height: 1.4;
      }
  }
  
  
  // Styles for the empty state
  .empty-state-content {
    // Centering is handled by d-flex utilities in the template
  }
  
  // Placeholder style (optional)
  .initializing-placeholder {
    // Styles for the initializing state with spinner
  }
  
  // Progress bar alignment if using v-card loading prop (usually handles itself)
  .v-card--loading {
    // Potential overrides if needed
  }
  </style>