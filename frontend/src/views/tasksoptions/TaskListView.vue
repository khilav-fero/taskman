<template>
  <v-container fluid class="pa-md-6 pa-4">
    <div class="d-flex justify-space-between align-center mb-6">
      <h1 class="text-h4 font-weight-medium">Tasks</h1>
    </div>

    <v-card
      variant="flat"
      :color="$vuetify.theme.current.colors.surface"
      rounded="lg"
      class="border flex-grow-1 d-flex flex-column"
    >
      <v-card-title class="pa-4 d-flex justify-space-between align-center">
        <span>Task List</span>
        <v-progress-circular
          v-if="isLoadingTasks"
          indeterminate
          color="primary"
          size="24"
        ></v-progress-circular>
      </v-card-title>
      <v-divider></v-divider>

      <v-card-text class="pa-0 flex-grow-1" style="overflow-y: auto;">
        <v-alert
          v-if="errorLoadingTasks && !isLoadingTasks"
          type="error"
          variant="tonal"
          closable
          class="ma-4"
          @update:modelValue="errorLoadingTasks = null"
          title="Error Loading Tasks"
          icon="mdi-alert-circle-outline"
          border="start"
          elevation="2"
        >
          {{ errorLoadingTasks }}
        </v-alert>

        <div
          v-else-if="!isLoadingTasks && tasksList.length === 0"
          class="text-center text-medium-emphasis pa-8 d-flex flex-column justify-center align-center fill-height"
        >
          <v-icon size="48" class="mb-2">mdi-format-list-checks</v-icon>
          <p>No tasks currently available.</p>
        </div>

        <v-list v-else class="py-0">
          <template v-for="(task, index) in tasksList" :key="task.id">
            <v-list-item class="py-3 px-4">
              <div>
                <div class="d-flex justify-space-between align-start mb-2">
                  <div class="flex-grow-1 mr-sm-4 mr-2">
                    <v-list-item-title
                      class="text-h6"
                      style="white-space: normal; word-break: break-word; line-height: 1.4;"
                    >
                      {{ task.title }}
                    </v-list-item-title>
                  </div>
                  <div class="d-flex ga-2 flex-shrink-0 align-self-start text-caption">
                    <span class="mr-2">Status: {{ task.status || 'N/A' }}</span>
                    <span>Priority: {{ task.priority || 'N/A' }}</span>
                  </div>
                </div>

                <v-list-item-subtitle
                  v-if="task.description"
                  class="text-body-2 mb-3"
                  style="white-space: normal; word-break: break-word;"
                >
                  {{ task.description }}
                </v-list-item-subtitle>
                <v-list-item-subtitle v-else class="text-disabled font-italic text-body-2 mb-3">
                  No description provided.
                </v-list-item-subtitle>

                <v-row dense class="text-caption text-medium-emphasis">
                  <v-col cols="12" sm="6" md="auto" class="d-flex align-center py-1">
                    <v-icon start size="x-small">mdi-account-outline</v-icon>
                    <span v-if="task.assignee">Assignee: {{ task.assignee.username }}</span>
                    <span v-else class="font-italic">Unassigned</span>
                  </v-col>

                  <v-col cols="12" sm="6" md="auto" class="d-flex align-center py-1">
                    <v-icon start size="x-small">mdi-calendar-clock-outline</v-icon>
                    <span v-if="task.deadline">Deadline: {{ task.deadline }}</span>
                    <span v-else class="font-italic">No Deadline</span>
                  </v-col>

                  <v-col cols="12" sm="6" md="auto" class="d-flex align-center py-1">
                    <v-icon start size="x-small">mdi-account-edit-outline</v-icon>
                    <span v-if="task.creator">Creator: {{ task.creator.username }}</span>
                    <span v-else class="font-italic">Creator Unknown</span>
                  </v-col>

                  <v-col cols="12" sm="6" md="auto" class="d-flex align-center py-1">
                    <v-icon start size="x-small">mdi-clock-plus-outline</v-icon>
                    <span v-if="task.created_at">Created: {{ task.created_at }}</span>
                    <span v-else class="font-italic">Creation Date N/A</span>
                  </v-col>
                </v-row>
              </div>
            </v-list-item>
            <v-divider v-if="index < tasksList.length - 1"></v-divider>
          </template>
        </v-list>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { fetchTasks } from '@/services/taskService';

export default {
  name: 'TaskListView',
  data() {
    return {
      tasksList: [],
      isLoadingTasks: false,
      errorLoadingTasks: null,
    };
  },
  methods: {
    async loadTasks() {
      this.isLoadingTasks = true;
      this.errorLoadingTasks = null;
      try {
        const responseData = await fetchTasks();
        if (responseData && Array.isArray(responseData.results)) {
          this.tasksList = responseData.results;
        } else if (Array.isArray(responseData)) {
          this.tasksList = responseData;
        } else {
          this.tasksList = [];
        }
      } catch (err) {
        this.errorLoadingTasks = err.message || 'Failed to load tasks.';
        this.tasksList = [];
      } finally {
        this.isLoadingTasks = false;
      }
    }
  },
  async mounted() {
    await this.loadTasks();
  }
};
</script>