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
                {{ formatHistoryTimestamp(entry.timestamp) }}
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
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  import { fetchTaskHistory } from '@/services/taskService';
  
  const props = defineProps({
    taskId: {
      type: [String, Number],
      required: true,
    },
  });
  
  const historyEntries = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  
  const loadHistory = async () => {
    if (!props.taskId) {
      historyEntries.value = [];
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      const data = await fetchTaskHistory(props.taskId);
      historyEntries.value = data.results || [];
    } catch (err) {
      console.error("Failed to load task history:", err);
      error.value = err?.detail || err?.message || "Could not load task history. Please try again.";
       historyEntries.value = [];
    } finally {
      isLoading.value = false;
    }
  };
  
  const formatHistoryTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: 'numeric', minute: '2-digit', hour12: true
      });
    } catch (e) {
      return timestamp;
    }
  };
  
  onMounted(() => {
    loadHistory();
  });
  
  watch(() => props.taskId, (newTaskId) => {
    if (newTaskId) {
      loadHistory();
    } else {
      historyEntries.value = [];
    }
  });
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