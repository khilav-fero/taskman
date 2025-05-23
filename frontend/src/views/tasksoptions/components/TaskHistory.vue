<template>
    <div class="task-history-container pa-4">
      <v-progress-linear
        v-if="isLoading"
        indeterminate
        color="primary"
        class="mb-4"
      ></v-progress-linear>
  
      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4"
      >
        {{ error }}
      </v-alert>
  
      <div v-if="!isLoading && !error">
        <v-list v-if="historyEntries.length > 0" lines="two" density="compact">
          <template v-for="(entry, index) in historyEntries" :key="entry.id">
            <v-list-item class="history-entry">
              <template v-slot:prepend>
                <v-icon color="grey-darken-1" class="mr-3">mdi-history</v-icon>
              </template>
              <v-list-item-title class="text-body-2 font-weight-medium">
                {{ entry.change_description }}
              </v-list-item-title>
              <v-list-item-subtitle class="text-caption text-medium-emphasis">
                <!-- TEMP DEBUGGING STATEMENTS ADDDED BELOW -->
                By: {{ entry.user?.username || 'ENTRY NOT RECORDED' }} - {{ formatHistoryTimestamp(entry.timestamp) }}
                <!-- By: {{ entry.user?.username || 'ENTRY NOT RECORDED' }} - {{ formatHistoryTimestamp(entry.timestamp) }} -->
              </v-list-item-subtitle>
            </v-list-item>
            <v-divider v-if="index < historyEntries.length - 1" class="my-1"></v-divider>
          </template>
        </v-list>
        <div v-else class="text-center text-medium-emphasis pa-5">
          <v-icon size="48" class="mb-2">mdi-archive-alert-outline</v-icon>
          <p>No history found for this task.</p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { fetchTaskHistory } from '@/services/taskService';
  
  export default {
    name: 'TaskHistory', 
    props: {
      taskId: {
        type: [String, Number],
        required: true,
      },
    },
    data() {
      return {
        historyEntries: [],
        isLoading: false,
        error: null,
      };
    },
    watch: {
      taskId(newTaskId) {
        if (newTaskId) {
          this.loadHistory();
        } else {
          this.historyEntries = [];
        }
      }
    },
    methods: {
      async loadHistory() {
        if (!this.taskId) {
          this.historyEntries = [];
          return;
        }
        this.isLoading = true;
        this.error = null;
        try {
          const data = await fetchTaskHistory(this.taskId);
          this.historyEntries = data.results || [];
        } catch (err) {
          console.error("Failed to load task history:", err);
          this.error = err?.detail || err?.message || "Could not load task history. Please try again.";
          this.historyEntries = [];
        } finally {
          this.isLoading = false;
        }
      },
      formatHistoryTimestamp(timestamp) {
        if (!timestamp) return '';
        try {
          return new Date(timestamp).toLocaleString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: 'numeric', minute: '2-digit', hour12: true
          });
        } catch (e) {
          return timestamp;
        }
      }
    },
    mounted() {
      this.loadHistory();
    }
  };
  </script>
  
  <style lang="scss" scoped>
  .task-history-container {
    min-height: 200px;
    max-height: 400px; 
    overflow-y: auto;
  }
  .history-entry {
    padding-left: 0;
    padding-right: 0;
  }
  .v-list-item-title {
    white-space: normal;
    line-height: 1.3;
  }
  .v-list-item-subtitle {
    white-space: normal;
    line-height: 1.3;
  }
  </style>