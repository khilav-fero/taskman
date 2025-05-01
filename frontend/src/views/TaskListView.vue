<template>
    <v-container fluid class="pa-4 task-list-view-container">
      <div class="d-flex justify-space-between align-center mb-4">
        <h1>My Tasks</h1>
      </div>
  
      <v-progress-linear
        v-if="tasksStore.getTasksLoading"
        indeterminate
        color="primary"
        class="mb-1"
        height="6"
      ></v-progress-linear>
  
      <v-alert
        v-if="tasksStore.getTasksError && !tasksStore.getTasksLoading"
        type="error"
        variant="tonal"
        closable
        class="mb-4"
        title="Error Loading Tasks"
        @update:modelValue="clearTaskError"
      >
        {{ tasksStore.getTasksError }}
      </v-alert>
  
      <!-- Ag-Grid Table Container -->
      <div
        v-if="componentReady"
        class="ag-theme-material grid-container"
      >
        <ag-grid-vue
          :columnDefs="columnDefs"
          :rowData="gridRowData"
          :defaultColDef="defaultColDef"
          :modules="agGridModules"
          rowSelection="multiple"
          :animateRows="true"
          :pagination="true"
          :paginationPageSize="15"
          :suppressRowClickSelection="true"
          @grid-ready="onGridReady"
          style="width: 100%; height: 100%;"
        />
      </div>
  
      <div v-else-if="!tasksStore.getTasksLoading && tasksStore.getTasksList.length === 0 && !tasksStore.getTasksError">
        <p>No tasks found.</p>
      </div>
  
      <div v-else-if="!tasksStore.getTasksLoading && !tasksStore.getTasksError">
        <p>Initializing...</p>
      </div>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useTasksStore } from '@/store/tasks';
  import { AgGridVue } from "ag-grid-vue3";
  
  // --- AG Grid Styles ---
  import "ag-grid-community/styles/ag-grid.css";
  import "ag-grid-community/styles/ag-theme-material.css";
  
  // ✅ Updated AG Grid import
  import { ClientSideRowModelModule } from "ag-grid-community";
  
  // ✅ Define modules
  const agGridModules = [ClientSideRowModelModule];
  
  // --- Pinia Store ---
  const tasksStore = useTasksStore();
  
  // --- Component State ---
  const gridApi = ref(null);
  const componentReady = ref(false);
  
  // --- AG Grid Configuration ---
  const defaultColDef = ref({
    sortable: true,
    filter: true,
    resizable: true,
    floatingFilter: true,
    flex: 1,
    minWidth: 100,
  });
  
  const columnDefs = ref([
    { headerName: 'Title', field: 'title', filter: 'agTextColumnFilter', flex: 2, wrapText: true, autoHeight: true, minWidth: 200 },
    { headerName: 'Status', field: 'status', filter: true, width: 150, flex: 0 },
    {
      headerName: 'Priority', field: 'priority', filter: 'agNumberColumnFilter', width: 120, flex: 0,
      valueFormatter: params => {
        const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' };
        return priorityMap[params.value] || params.value?.toString() || '';
      }
    },
    {
      headerName: 'Assignee', field: 'assignee.username',
      valueGetter: params => params.data.assignee?.username || 'Unassigned',
      filter: true, width: 150
    },
    {
      headerName: 'Creator', field: 'creator.username',
      valueGetter: params => params.data.creator?.username || 'Unknown',
      filter: true, width: 150
    },
    {
      headerName: 'Deadline', field: 'deadline', filter: 'agDateColumnFilter', width: 150, flex: 0,
      valueFormatter: params => params.value ? new Date(params.value).toLocaleDateString() : ''
    },
    {
      headerName: 'Created', field: 'created_at', filter: 'agDateColumnFilter', sort: 'desc', width: 180, flex: 0,
      valueFormatter: params => params.value ? new Date(params.value).toLocaleString() : ''
    },
  ]);
  
  // --- Computed Grid Data ---
  const gridRowData = computed(() => {
    return tasksStore.getTasksList || [];
  });
  
  // --- AG Grid Ready Callback ---
  const onGridReady = (params) => {
    console.log('AG Grid is ready.');
    gridApi.value = params.api;
  };
  
  // --- Data Loading ---
  const loadTasks = async () => {
    console.log('TaskListView: Attempting to fetch tasks...');
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
  });
  </script>
  
  <style lang="scss" scoped>
  .task-list-view-container {
    height: calc(100vh - 64px);
    display: flex;
    flex-direction: column;
  }
  
  .grid-container {
    flex-grow: 1;
    width: 100%;
    height: 100%;
  }
  
  :deep(.ag-cell-wrap-text) {
    white-space: normal !important;
    line-height: 1.4 !important;
    padding-top: 4px !important;
    padding-bottom: 4px !important;
  }
  </style>
  