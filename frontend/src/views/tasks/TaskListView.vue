<template>
  <v-container fluid class="pa-md-6 pa-4 task-list-view-container d-flex flex-column">
    <div class="d-flex justify-space-between align-center mb-4 flex-wrap ga-sm-4 ga-3 flex-shrink-0">
      <h1 class="text-h4 font-weight-medium header-title">TASKS</h1>
    </div>

    <v-card
      :loading="tasksLoading"
      variant="flat"
      class="flex-grow-1 d-flex flex-column card-container"
      :color="$vuetify.theme.current.colors.surface"
      rounded="lg"
    >
      <div v-if="showErrorAlert" class="card-header-section flex-shrink-0">
        <v-alert
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
          v-model:items-per-page="itemsPerPage"
          v-model:page="currentPage"
          v-model:sort-by="sortBy"
          :headers="dataTableHeaders"
          :items="tasksList"
          :items-length="totalTasks"
          :loading="tasksLoading"
          item-value="id"
          class="flex-grow-1 task-data-table user-data-table"
          fixed-header
          height="100%"
          density="comfortable"
          hover
          @update:page="updatePagination"
          
          @update:itemsPerPage="updatePagination"
          @update:options="handleOptionsUpdate"
          @click:row="(_, { item }) => openDetailDialog(item)"
          :row-props="() => ({ class: 'clickable-row' })"
        >
          <template v-slot:top>
            <div class="d-flex justify-space-between align-center pa-4 flex-wrap ga-3 data-table-controls-header">
              <div class="d-flex align-center flex-wrap ga-3">
                <v-text-field
                  v-model="search"
                  label="Search Title/Desc"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  class="search-field filter-control"
                  color="primary"
                  bg-color="transparent"
                  @input="onSearchInput"
                  style="max-width: 280px;"
                  @click.stop
                ></v-text-field>

                <v-select
                  v-model="selectedStatus"
                  label="Status"
                  :items="statusChoices"
                  item-title="text"
                  item-value="value"
                  multiple
                  clearable
                  chips
                  closable-chips
                  variant="outlined"
                  density="compact"
                  hide-details
                  class="filter-control"
                  color="primary"
                  bg-color="transparent"
                  style="max-width: 220px;"
                  @click.stop
                ></v-select>

                <v-select
                  v-model="selectedPriority"
                  label="Priority"
                  :items="priorityChoices"
                  item-title="text"
                  item-value="value"
                  multiple
                  clearable
                  chips
                  closable-chips
                  variant="outlined"
                  density="compact"
                  hide-details
                  class="filter-control"
                  color="primary"
                  bg-color="transparent"
                  style="max-width: 200px;"
                  @click.stop
                ></v-select>
              </div>

              <v-btn
                v-if="canManageTasks"
                color="primary"
                prepend-icon="mdi-plus"
                @click.stop="openCreateDialog"
                variant="flat"
                class="create-task-btn add-user-btn flex-shrink-0"
                min-width="150"
              >
                Create Task
              </v-btn>

            </div>
            <v-divider v-if="!tasksLoading && !showErrorAlert"></v-divider>
          </template>

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
                {{ formatShortDate(item.deadline) }}
            </span>
          </template>
          <template v-slot:item.created_at="{ item }">
             <span class="data-table-text-secondary">
                {{ formatDateTime(item.created_at) }}
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
                <template v-if="search">No tasks found matching your search and filter criteria.</template>
                <template v-else-if="anyFiltersActive">No tasks found matching your filter criteria.</template>
                <template v-else>No tasks available.</template>
              </div>
               <p class="text-body-2 text-medium-emphasis mt-1" v-if="!search && !anyFiltersActive && canManageTasks">Try creating a new task to get started!</p>
               <v-btn v-if="anyFiltersActive" class="mt-4" variant="text" color="primary" @click="resetFilters">Clear Filters</v-btn>
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
          v-else-if="!tasksLoading && !showErrorAlert && !componentReady"
          class="state-content-message"
        >
          <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
          <p class="text-body-1 text-medium-emphasis mt-4">Initializing Task List...</p>
        </div>
      </div>
    </v-card>

    <v-dialog v-model="isFormDialogOpen" persistent max-width="700px" @keydown.esc="closeFormDialog" scrollable>
      <TaskForm
        v-if="isFormDialogOpen"
        :initial-data="editingTask"
        :loading="formSubmitting"
        :error="formError"
        @submit="onFormSubmit"
        @cancel="closeFormDialog"
        @clear-form-error="clearFormError"
        key="task-form-component"
      />
    </v-dialog>

    <TaskDeleteConfirmationDialog
      v-if="isConfirmDeleteDialogOpen"
      v-model="isConfirmDeleteDialogOpen"
      :task-to-delete="taskToDelete"
      @confirmed="handleTaskDeleted"
      @error="handleDeleteError"
    />

    <v-dialog v-model="isDetailDialogOpen" max-width="800px" scrollable @keydown.esc="closeDetailDialog">
        <v-card v-if="selectedTaskForDetail">
            <v-card-title class="d-flex justify-space-between align-center pa-4">
                <span class="text-h5">
                  {{
                    detailDialogTab === 'details' && isEditingDetail ? 'Edit Task Details' :
                    (detailDialogTab === 'details' ? 'Task Details' :
                    (detailDialogTab === 'history' ? 'Task History' :
                    (detailDialogTab === 'comments' ? 'Task Comments' : 'Task Collaborators')))
                  }}
                </span>
                 <div class="dialog-actions">
                    <v-btn
                      v-if="canManageTasks && detailDialogTab === 'details' && !isEditingDetail"
                      color="primary"
                      variant="text"
                      @click="isEditingDetail = true"
                      icon="mdi-pencil-outline"
                      density="comfortable"
                    >
                       <v-icon>mdi-pencil-outline</v-icon>
                        <v-tooltip activator="parent" location="bottom">Edit Task</v-tooltip>
                    </v-btn>
                    <v-btn icon="mdi-close" variant="text" @click="closeDetailDialog" density="comfortable">
                        <v-icon>mdi-close</v-icon>
                        <v-tooltip activator="parent" location="bottom">Close</v-tooltip>
                    </v-btn>
                 </div>
            </v-card-title>
            <v-divider></v-divider>

            <v-tabs v-model="detailDialogTab" color="primary" grow>
                <v-tab value="details">Details</v-tab>
                <v-tab value="collaborators">Collaborators</v-tab>
                <v-tab value="comments">Comments</v-tab>
                <v-tab value="history">History</v-tab>
            </v-tabs>
            <v-divider></v-divider>

            <v-card-text class="pa-0 dialog-content-wrapper">
              <v-window v-model="detailDialogTab">
                <v-window-item value="details" class="dialog-window-item">
                  <div v-if="!isEditingDetail" class="pa-5">
                       <v-row dense>
                          <v-col cols="12" md="8">
                              <h3 class="text-h6 mb-1">{{ selectedTaskForDetail.title }}</h3>
                              <p v-if="selectedTaskForDetail.description" class="text-body-1 text-medium-emphasis" style="white-space: pre-wrap;">{{ selectedTaskForDetail.description }}</p>
                              <p v-else class="text-body-1 text-disabled">No description provided.</p>
                          </v-col>
                          <v-col cols="12" md="4">
                             <v-list density="compact" class="detail-list bg-transparent">
                                  <v-list-item prepend-icon="mdi-list-status" title="Status">
                                      <template v-slot:append>
                                           <v-chip :color="getStatusColor(selectedTaskForDetail.status)" size="small" label variant="flat" class="data-table-chip status-chip text-uppercase">
                                              {{ selectedTaskForDetail.status.replace('_', ' ') }}
                                           </v-chip>
                                      </template>
                                  </v-list-item>
                                  <v-list-item prepend-icon="mdi-priority-high" title="Priority">
                                      <template v-slot:append>
                                          <v-chip :color="getPriorityColor(selectedTaskForDetail.priority)" size="small" label variant="tonal" class="data-table-chip">
                                            {{ formatPriority(selectedTaskForDetail.priority) }}
                                          </v-chip>
                                      </template>
                                  </v-list-item>
                                  <v-list-item prepend-icon="mdi-account-outline" title="Assignee">
                                      <template v-slot:append>
                                          <span :class="{'text-disabled': !selectedTaskForDetail.assignee}">{{ selectedTaskForDetail.assignee?.username || 'Unassigned' }}</span>
                                      </template>
                                  </v-list-item>
                                  <v-list-item prepend-icon="mdi-calendar-clock" title="Deadline">
                                      <template v-slot:append>
                                          <span>{{ formatFullDate(selectedTaskForDetail.deadline) }}</span>
                                      </template>
                                  </v-list-item>
                             </v-list>
                          </v-col>
                       </v-row>
                       <v-divider class="my-4"></v-divider>
                        <v-row dense>
                             <v-col cols="12" sm="6">
                                 <v-list density="compact" class="detail-list bg-transparent">
                                      <v-list-item prepend-icon="mdi-account-edit-outline" title="Created By">
                                          <template v-slot:append>
                                              <span>{{ selectedTaskForDetail.creator?.username || 'Unknown' }}</span>
                                          </template>
                                      </v-list-item>
                                 </v-list>
                             </v-col>
                              <v-col cols="12" sm="6">
                                 <v-list density="compact" class="detail-list bg-transparent">
                                      <v-list-item prepend-icon="mdi-clock-plus-outline" title="Created On">
                                          <template v-slot:append>
                                              <span>{{ formatDateTime(selectedTaskForDetail.created_at) }}</span>
                                          </template>
                                      </v-list-item>
                                 </v-list>
                             </v-col>
                        </v-row>
                  </div>
                  <div v-else>
                      <TaskForm
                          :initial-data="selectedTaskForDetail"
                          :loading="detailFormSubmitting"
                          :error="detailFormError"
                          @submit="onDetailFormSubmit"
                          @cancel="onDetailFormCancel"
                          @clear-form-error="clearDetailFormError"
                          key="task-detail-form-component"
                          :is-dialog-mode="true"
                      />
                  </div>
                </v-window-item>
                <v-window-item value="collaborators" class="dialog-window-item pa-4">
                    <TaskCollaborators
                        v-if="selectedTaskForDetail && detailDialogTab === 'collaborators'"
                        :task-id="selectedTaskForDetail.id"
                        :current-collaborators="selectedTaskForDetail.collaborators || []"
                        :can-manage="canManageTasks"
                        @collaborator-added="handleCollaboratorChange"
                        @collaborator-removed="handleCollaboratorChange"
                        @error="(msg) => taskCollaboratorError = msg"
                        :key="selectedTaskForDetail.id + '-collaborators'"
                    />
                    <v-alert v-if="taskCollaboratorError" type="error" density="compact" variant="tonal" class="mt-3">
                        {{ taskCollaboratorError }}
                    </v-alert>
                </v-window-item>
                <v-window-item value="comments" class="dialog-window-item">
                   <TaskComments v-if="selectedTaskForDetail && detailDialogTab === 'comments'" :task-id="selectedTaskForDetail.id" :key="selectedTaskForDetail.id + '-comments'" />
                </v-window-item>
                <v-window-item value="history" class="dialog-window-item">
                   <TaskHistory v-if="selectedTaskForDetail && detailDialogTab === 'history'" :task-id="selectedTaskForDetail.id" :key="selectedTaskForDetail.id + '-history'" />
                </v-window-item>
              </v-window>
            </v-card-text>
        </v-card>
    </v-dialog>

    <v-tooltip location="bottom"></v-tooltip>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, inject, watch, shallowRef, nextTick } from 'vue';
import { fetchTasks, createTask as createTaskApi, updateTask as updateTaskApi, deleteTaskApi as deleteTaskServiceApi } from '@/services/taskService';
import TaskForm from '@/views/tasks/components/TaskForm.vue';
import TaskDeleteConfirmationDialog from './components/TaskDeleteConfirmationDialog.vue';
import TaskHistory from './components/TaskHistory.vue';
import TaskComments from './components/TaskComments.vue';
import TaskCollaborators from './components/TaskCollaborators.vue';
import { debounce } from 'lodash';
import { VTooltip } from 'vuetify/components/VTooltip';

const currentUser = inject('currentUser', ref(null));

const componentReady = ref(false);
const itemsPerPage = ref(15);
const currentPage = ref(1);
const totalTasks = ref(0);

const search = ref('');
const selectedStatus = ref([]);
const selectedPriority = ref([]);

const tasksList = ref([]);
const tasksLoading = ref(false);
const tasksError = ref(null);
const formSubmitting = ref(false);
const formError = ref(null);

const isConfirmDeleteDialogOpen = ref(false);
const taskToDelete = ref(null);

const isDetailDialogOpen = ref(false);
const selectedTaskForDetail = ref(null);
const isEditingDetail = ref(false);
const detailFormSubmitting = ref(false);
const detailFormError = ref(null);
const detailDialogTab = ref('details');
const taskCollaboratorError = ref(null);

const sortBy = shallowRef([]);

const dataTableHeaders = ref([
  {
    title: 'Title & Description', key: 'title', sortable: true, class: 'text-wrap', minWidth: '300px', width: '35%',
    sort: (titleA, titleB) => {
      const valA = titleA?.toLowerCase() ?? null;
      const valB = titleB?.toLowerCase() ?? null;
      if (valA === null && valB !== null) return 1;
      if (valA !== null && valB === null) return -1;
      if (valA === null && valB === null) return 0;
      return valA < valB ? -1 : (valA > valB ? 1 : 0);
    }
  },
  {
    title: 'Status', key: 'status', sortable: true, width: '130px', align: 'center',
    sort: (statusA, statusB) => {
      const valA = statusA?.toLowerCase() ?? null;
      const valB = statusB?.toLowerCase() ?? null;
      if (valA === null && valB !== null) return 1;
      if (valA !== null && valB === null) return -1;
      if (valA === null && valB === null) return 0;
      return valA < valB ? -1 : (valA > valB ? 1 : 0);
    }
  },
  {
    title: 'Priority', key: 'priority', sortable: true, width: '120px', align: 'center',
    sort: (priorityA, priorityB) => {
      const valA = (priorityA === undefined || priorityA === null) ? null : Number(priorityA);
      const valB = (priorityB === undefined || priorityB === null) ? null : Number(priorityB);
      if (valA === null && valB !== null) return 1;
      if (valA !== null && valB === null) return -1;
      if (valA === null && valB === null) return 0;
      return valA - valB;
    }
  },
  {
    title: 'Assignee', key: 'assignee', sortable: true, value: item => item.assignee?.username, width: '160px',
    sort: (assigneeA, assigneeB) => {
      const usernameA = assigneeA?.username?.toLowerCase() || null;
      const usernameB = assigneeB?.username?.toLowerCase() || null;
      if (usernameA === null && usernameB !== null) return 1;
      if (usernameA !== null && usernameB === null) return -1;
      if (usernameA === null && usernameB === null) return 0;
      return usernameA < usernameB ? -1 : (usernameA > usernameB ? 1 : 0);
    }
  },
  {
    title: 'Deadline', key: 'deadline', sortable: true, width: '140px',
    sort: (deadlineA, deadlineB) => {
      const dateA = deadlineA ? new Date(deadlineA + 'T00:00:00Z').getTime() : null;
      const dateB = deadlineB ? new Date(deadlineB + 'T00:00:00Z').getTime() : null;
      if (dateA === null && dateB !== null) return 1;
      if (dateA !== null && dateB === null) return -1;
      if (dateA === null && dateB === null) return 0;
      return dateA - dateB;
    }
  },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '120px' }
]);


const statusChoices = [
  { text: 'To-Do', value: 'TODO' },
  { text: 'In-Progress', value: 'INPROGRESS' },
  { text: 'Code Review', value: 'REVIEW' },
  { text: 'Done', value: 'DONE' },
];

const priorityChoices = [
  { text: 'Low', value: 1 },
  { text: 'Medium', value: 2 },
  { text: 'High', value: 3 },
  { text: 'Urgent', value: 4 },
];

const hasTasks = computed(() => tasksList.value.length > 0);
const showErrorAlert = computed(() => !!tasksError.value && !tasksLoading.value);
const showTable = computed(() =>
  componentReady.value && !tasksLoading.value && !showErrorAlert.value && totalTasks.value > 0
);
const showEmptyState = computed(() =>
  componentReady.value && !tasksLoading.value && !showErrorAlert.value && totalTasks.value === 0 && !anyFiltersActive.value
);
const anyFiltersActive = computed(() => {
  return (
    !!search.value ||
    selectedStatus.value.length > 0 ||
    selectedPriority.value.length > 0
  );
});
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
  if (lowerStatus === 'done') return 'success';
  if (lowerStatus === 'in progress') return 'primary';
  if (lowerStatus === 'todo' || lowerStatus === 'to do') return 'info';
   if (lowerStatus === 'review' || lowerStatus === 'code review') return 'purple';
  return 'blue-grey-lighten-1';
};
const formatShortDate = (dateString) => {
  if (!dateString) return '–';
  try {
    return new Date(dateString + 'T00:00:00Z').toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
  } catch (e) {
    return 'Invalid Date';
  }
};
const formatFullDate = (dateString) => {
  if (!dateString) return 'Not Set';
   try {
    return new Date(dateString + 'T00:00:00Z').toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
   } catch (e) {
    return 'Invalid Date';
  }
};
const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return '–';
    try {
        return new Date(dateTimeString).toLocaleString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: 'numeric', minute: '2-digit', hour12: true
        });
    } catch (e) {
        return 'Invalid Date';
    }
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
  taskToDelete.value = { ...task };
  formError.value = null;
  isConfirmDeleteDialogOpen.value = true;
};
const handleTaskDeleted = async () => {
  isConfirmDeleteDialogOpen.value = false;
  taskToDelete.value = null;
  await loadTasks();
};
const handleDeleteError = (errorMessage) => {
  console.error("Delete operation failed (TaskListView):", errorMessage);
};

const openDetailDialog = (taskItem) => {
    selectedTaskForDetail.value = { ...taskItem };
    isEditingDetail.value = false;
    detailFormError.value = null;
    detailDialogTab.value = 'details';
    taskCollaboratorError.value = null;
    isDetailDialogOpen.value = true;
};

const closeDetailDialog = () => {
    isDetailDialogOpen.value = false;
    selectedTaskForDetail.value = null;
    isEditingDetail.value = false;
    detailFormError.value = null;
    detailDialogTab.value = 'details';
    taskCollaboratorError.value = null;
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

const onDetailFormSubmit = async (formDataFromForm) => {
    if (!selectedTaskForDetail.value?.id) return;

    detailFormSubmitting.value = true;
    detailFormError.value = null;
    let success = false;
    let updatedTaskData = null;

    try {
        updatedTaskData = await updateTaskApi(selectedTaskForDetail.value.id, formDataFromForm);
        success = true;
    } catch (err) {
        detailFormError.value = err?.detail || err?.message || 'Failed to update task details.';
        console.error("Error updating task details:", err);
    } finally {
        detailFormSubmitting.value = false;
    }

    if (success) {
        await loadTasks();
        const freshTask = tasksList.value.find(t => t.id === selectedTaskForDetail.value.id);
        if (freshTask) {
          selectedTaskForDetail.value = { ...freshTask };
        } else {
          selectedTaskForDetail.value = { ...selectedTaskForDetail.value, ...updatedTaskData };
        }

        isEditingDetail.value = false;
        detailFormError.value = null;
    }
};

const onDetailFormCancel = () => {
    isEditingDetail.value = false;
    detailFormError.value = null;
};

const clearDetailFormError = () => {
  detailFormError.value = null;
};

const handleCollaboratorChange = async () => {
    taskCollaboratorError.value = null;
    await loadTasks();
    if (selectedTaskForDetail.value) {
        const freshTask = tasksList.value.find(t => t.id === selectedTaskForDetail.value.id);
        if (freshTask) {
            selectedTaskForDetail.value = { ...freshTask };
        } else {
            closeDetailDialog();
        }
    }
};


const buildFilterParams = () => {
  const params = {
    page: currentPage.value,
    page_size: itemsPerPage.value,
  };

  if (search.value) {
    params.search = search.value;
  }

  if (selectedStatus.value && selectedStatus.value.length > 0) {
    params.status__in = selectedStatus.value.join(',');
  }

  if (selectedPriority.value && selectedPriority.value.length > 0) {
     params.priority__in = selectedPriority.value.join(',');
  }

  // Removed ordering parameter for client-side sorting
  // if (sortBy.value && sortBy.value.length > 0) {
  //   const sortItem = sortBy.value[0];
  //   if (sortItem && sortItem.key) {
  //       params.ordering = (sortItem.order === 'desc' ? '-' : '') + sortItem.key;
  //   }
  // } else {
  //     params.ordering = '-priority,-created_at';
  // }

  return params;
};

const loadTasks = async () => {
  tasksLoading.value = true;
  tasksError.value = null;
  try {
    const params = buildFilterParams();
    const responseData = await fetchTasks(params);

    if (responseData && typeof responseData === 'object' && Array.isArray(responseData.results)) {
      tasksList.value = responseData.results;
      totalTasks.value = responseData.count;
    } else {
      tasksList.value = [];
      totalTasks.value = 0;
      console.warn("Received task data in unexpected format:", responseData);
    }
  } catch (err)
{
    tasksError.value = err?.detail || err?.message || 'Could not load tasks.';
    console.error('TaskListView: Could not load tasks.', err);
    tasksList.value = [];
    totalTasks.value = 0;
  } finally {
    tasksLoading.value = false;
    if (!componentReady.value) {
      componentReady.value = true;
    }
  }
};

const updatePagination = () => {
    loadTasks();
};

const debouncedLoadTasks = debounce(async () => {
  await nextTick();
  loadTasks();
}, 50);

const reloadData = (resetPage = true) => {
  if (resetPage && currentPage.value !== 1) {
    currentPage.value = 1; // This will trigger loadTasks via watch on currentPage or @update:page
  } else {
    debouncedLoadTasks();
  }
};

// This function is no longer directly called by @update:sortBy
// v-model:sort-by="sortBy" handles updating sortBy directly.
// The v-data-table will use the custom sort functions in headers.
// const updateSort = (newSortState) => {
//   sortBy.value = newSortState;
//   // No reloadData() for client-side sorting of the current page's data
// };

const handleOptionsUpdate = (options) => {

};


const onSearchInput = debounce(() => {
  reloadData(true);
}, 350);

watch([selectedStatus, selectedPriority], () => {
  reloadData(true);
});

watch(isDetailDialogOpen, (newValue) => {
  if (!newValue) {
    detailDialogTab.value = 'details';
    isEditingDetail.value = false;
    taskCollaboratorError.value = null;
  } else {
    taskCollaboratorError.value = null;
  }
});

watch(detailDialogTab, () => {
    taskCollaboratorError.value = null;
});

const resetFilters = () => {
  search.value = '';
  selectedStatus.value = [];
  selectedPriority.value = [];
  sortBy.value = []; // Clear client-side sort
  reloadData(true);
};

const clearComponentError = () => {
  tasksError.value = null;
};
const clearFormError = () => {
  formError.value = null;
};

onMounted(() => {
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
  padding: 4px 0px;
}

.table-and-state-wrapper {
  overflow: hidden;
  position: relative;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.add-user-btn {
  color: rgb(var(--v-theme-on-primary));
  font-weight: 500;
}

.data-table-controls-header {
  border-bottom: none;

  .filter-control {
    flex-grow: 0;
    flex-shrink: 1;
    min-width: 150px;

    :deep(.v-field) {
      background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
      border-radius: var(--v-border-radius-medium);
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
      box-shadow: 0 0 0 2px rgba(var(--v-theme-primary-rgb), 0.1);
    }
    :deep(.v-label.v-field-label) {
      color: rgba(var(--v-theme-on-surface), 0.65) !important;
      font-weight: 400;
      font-size: 0.9em;
    }
    :deep(.v-field--active .v-label.v-field-label) {
      color: rgb(var(--v-theme-primary)) !important;
    }
    :deep(input), :deep(.v-select__selection-text), :deep(.v-select__selection .v-chip) {
      color: rgb(var(--v-theme-on-surface)) !important;
       font-size: 0.95em;
    }
     :deep(.v-select__selection .v-chip) {
        font-size: 0.85em !important;
        height: 22px !important;
     }
    :deep(.v-field__prepend-inner .v-icon),
    :deep(.v-field__append-inner .v-icon) {
      color: rgba(var(--v-theme-on-surface), 0.5) !important;
    }
  }

  .search-field {
  }
}

.user-data-table {
  color: rgb(var(--v-theme-on-surface));
  border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);
  flex-grow: 1;
  display: flex;
  flex-direction: column;

  :deep(.v-data-table__wrapper) {
    overflow-y: auto;
    flex-grow: 1;
    min-height: 0;
     border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);
  }

  :deep(.v-data-table__top) {
      flex-shrink: 0;
      background-color: rgb(var(--v-theme-surface));
  }

  :deep(thead th) {
    position: sticky;
    top: 0;
    background-color: rgba(var(--v-theme-surface-rgb), 0.9) !important;
    backdrop-filter: blur(4px);
    z-index: 10;
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.1) !important;
    color: rgba(var(--v-theme-on-surface), 0.75) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    height: 48px !important;
  }

  :deep(tbody tr.clickable-row:hover) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.05) !important;
    cursor: pointer;
  }

  :deep(.v-data-table__td) {
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08) !important;
    padding: 12px 16px !important;
    font-size: 0.9rem;
    height: auto !important;
    vertical-align: top;
  }

  .data-table-text-primary {
    color: rgb(var(--v-theme-on-surface));
    line-height: 1.5;
    font-weight: 500;
    font-size: 0.95rem;
  }

  .data-table-text-secondary {
    color: rgba(var(--v-theme-on-surface), 0.75);
    line-height: 1.5;
    font-size: 0.875rem;
     &.text-disabled {
        font-style: italic;
        color: rgba(var(--v-theme-on-surface), 0.5);
     }
  }

  .task-title-cell {
    display: block;
    white-space: normal;
    word-break: break-word;
  }
  .task-description-cell {
    font-size: 0.875rem;
    margin-top: 4px;
    max-height: 3.8em;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    white-space: normal;
  }

  .data-table-chip {
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    padding: 3px 10px;
    height: 26px !important;
    letter-spacing: 0.02em;
    &.status-chip {
      color: rgb(var(--v-theme-on-primary)) !important;
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
    flex-shrink: 0;
    border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
    padding: 8px 0;
    background-color: rgb(var(--v-theme-surface));
    border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);

    .v-data-table-footer__items-per-page,
    .v-data-table-footer__info {
        color: rgba(var(--v-theme-on-surface), 0.75) !important;
        font-size: 0.875rem;
    }
     .v-data-table-footer__items-per-page {
        .v-select .v-field__input, .v-select .v-select__selection-text {
            color: rgba(var(--v-theme-on-surface), 0.9) !important;
            font-size: 0.875rem;
        }
        .v-select .v-field__outline { display: none; }
        .v-icon { color: rgba(var(--v-theme-on-surface), 0.65) !important; }
    }
     .v-pagination__item .v-btn { color: rgba(var(--v-theme-on-surface), 0.75) !important; }
     .v-pagination__item--is-active .v-btn { color: rgb(var(--v-theme-on-primary)) !important; }
     .v-pagination__prev .v-btn, .v-pagination__next .v-btn { color: rgba(var(--v-theme-on-surface), 0.75) !important; }
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
  min-height: 300px;

  .text-h6, .text-subtitle-1 {
     color: rgba(var(--v-theme-on-surface), 0.9);
  }
  .text-body-1, .text-body-2 {
     color: rgba(var(--v-theme-on-surface), 0.65);
  }
}

.dialog-title-error { color: rgb(var(--v-theme-error)) !important; }
.dialog-title-icon { color: rgb(var(--v-theme-error)) !important; }
.dialog-text-primary {
  color: rgb(var(--v-theme-on-surface));
  line-height: 1.6;
  strong {
    color: rgb(var(--v-theme-on-surface));
    font-weight: 500;
  }
}
.dialog-actions {
}
.dialog-btn-cancel {
  color: rgba(var(--v-theme-on-surface), 0.75);
  font-weight: 500;
  &:hover { color: rgb(var(--v-theme-on-surface)); }
}
.dialog-btn-confirm {
  color: rgb(var(--v-theme-on-error)) !important;
  font-weight: 500;
}

.detail-list {
    :deep(.v-list-item__prepend) {
        width: auto;
        align-items: center;
        .v-icon {
            margin-inline-end: 12px;
            opacity: 0.7;
        }
    }
    :deep(.v-list-item-title) {
        font-size: 0.875rem;
        font-weight: 500;
        color: rgba(var(--v-theme-on-surface), 0.7);
    }
    :deep(.v-list-item__append) {
        font-size: 0.9rem;
        color: rgb(var(--v-theme-on-surface));
        .text-disabled {
           font-style: italic;
           color: rgba(var(--v-theme-on-surface), 0.5);
        }
    }
     :deep(.v-list-item) {
        min-height: 38px;
    }
}
.dialog-content-wrapper {
  min-height: 300px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}
.dialog-window-item {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

</style>