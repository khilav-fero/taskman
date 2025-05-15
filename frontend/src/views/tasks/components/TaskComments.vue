<template>
    <div class="task-comments-container pa-4">
      <v-progress-linear
        v-if="isLoadingComments"
        indeterminate
        color="primary"
        class="mb-4"
      ></v-progress-linear>
  
      <v-alert
        v-if="fetchError"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4"
        closable
        @update:modelValue="fetchError = null"
      >
        {{ fetchError }}
      </v-alert>
  
       <v-alert
        v-if="deleteError"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4"
        closable
        @update:modelValue="deleteError = null"
      >
        {{ deleteError }}
      </v-alert>
  
      <div v-if="!isLoadingComments && !fetchError" class="comments-list-section">
        <v-list v-if="comments.length > 0" lines="three" density="compact" class="py-0">
          <template v-for="(comment, index) in comments" :key="comment.id">
            <v-list-item class="comment-item px-0">
              <template v-slot:prepend>
                <v-avatar color="grey-lighten-1" size="36" class="mr-3 mt-1">
                  <span class="text-caption text-white">
                    {{ comment.author?.username?.substring(0, 2).toUpperCase() || '??' }}
                  </span>
                </v-avatar>
              </template>
              <div class="comment-content-wrapper">
                <div class="d-flex align-center justify-space-between mb-1">
                  <div>
                      <span class="text-subtitle-3 font-weight-bold mr-2">{{ comment.author?.username || 'Unknown User' }}</span>
                      <span class="text-caption text-medium-emphasis">{{ formatCommentTimestamp(comment.created_at) }}</span>
                  </div>
                  <v-btn
                      v-if="canCurrentUserDelete(comment)"
                      icon="mdi-delete-outline"
                      variant="text"
                      size="x-large"
                      color="red"
                      @click="openDeleteConfirmDialog(comment)"
                      density="comfortable"
                      class="ml-auto comment-action-btn"
                  >
                      <v-icon size="small">mdi-delete-outline</v-icon>
                      <v-tooltip activator="parent" location="top">Delete Comment</v-tooltip>
                  </v-btn>
                </div>
                <p class="text-body-4 comment-text" style="white-space: pre-wrap;">{{ comment.text }}</p>
              </div>
            </v-list-item>
            <v-divider v-if="index < comments.length - 1" class="my-2"></v-divider>
          </template>
        </v-list>
        <div v-else class="text-center text-medium-emphasis pa-5">
          <v-icon size="48" class="mb-2">mdi-comment-processing-outline</v-icon>
          <p>No comments yet. Be the first to add one!</p>
        </div>
      </div>
  
      <v-divider class="my-4"></v-divider>
  
      <div class="add-comment-section">
        <v-textarea
          v-model="newCommentText"
          label="Add a comment..."
          variant="outlined"
          rows="3"
          auto-grow
          hide-details="auto"
          density="compact"
          class="mb-2"
          :error-messages="submitError ? [submitError] : []"
        ></v-textarea>
        <v-btn
          color="primary"
          variant="flat"
          @click="handleAddComment"
          :loading="isSubmittingComment"
          :disabled="!newCommentText.trim() || isSubmittingComment"
          class="add-comment-btn"
        >
          Add Comment
        </v-btn>
      </div>
  
      <v-dialog v-model="isDeleteConfirmOpen" max-width="450px" persistent>
        <v-card>
          <v-card-title class="text-h6 d-flex align-center">
            <v-icon color="warning" class="mr-2">mdi-alert-outline</v-icon>
            Confirm Deletion
          </v-card-title>
          <v-card-text>
            Are you sure you want to delete this comment? This action cannot be undone.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="closeDeleteConfirmDialog" :disabled="isDeletingComment">Cancel</v-btn>
            <v-btn color="error" variant="flat" @click="confirmDeleteComment" :loading="isDeletingComment">Delete</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch, inject, computed } from 'vue';
  import { fetchTaskComments, addTaskComment, deleteTaskComment } from '@/services/taskService';
  
  const props = defineProps({
    taskId: {
      type: [String, Number],
      required: true,
    },
  });
  
  const currentUser = inject('currentUser', ref(null));
  
  const comments = ref([]);
  const isLoadingComments = ref(false);
  const fetchError = ref(null);
  
  const newCommentText = ref('');
  const isSubmittingComment = ref(false);
  const submitError = ref(null);
  
  const isDeleteConfirmOpen = ref(false);
  const commentToDelete = ref(null);
  const isDeletingComment = ref(false);
  const deleteError = ref(null);
  
  
  const userRole = computed(() => currentUser.value?.profile?.role || null);
  
  const loadComments = async () => {
    if (!props.taskId) {
      comments.value = [];
      return;
    }
    isLoadingComments.value = true;
    fetchError.value = null;
    try {
      const data = await fetchTaskComments(props.taskId);
      comments.value = data.results || [];
    } catch (err) {
      console.error("Failed to load task comments:", err);
      fetchError.value = err?.detail || err?.message || "Could not load comments. Please try again.";
      comments.value = [];
    } finally {
      isLoadingComments.value = false;
    }
  };
  
  const handleAddComment = async () => {
    if (!newCommentText.value.trim()) return;
  
    isSubmittingComment.value = true;
    submitError.value = null;
    try {
      const newComment = await addTaskComment(props.taskId, { text: newCommentText.value.trim() });
      comments.value.push(newComment);
      newCommentText.value = '';
    } catch (err) {
      console.error("Failed to add comment:", err);
      submitError.value = err?.detail || err?.message || "Could not add comment. Please try again.";
    } finally {
      isSubmittingComment.value = false;
    }
  };
  
  const formatCommentTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffSeconds = Math.round((now - date) / 1000);
      const diffMinutes = Math.round(diffSeconds / 60);
      const diffHours = Math.round(diffMinutes / 60);
      const diffDays = Math.round(diffHours / 24);
  
      if (diffSeconds < 60) return 'just now';
      if (diffMinutes < 60) return `${diffMinutes}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays === 1) return 'yesterday';
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch (e) {
      return timestamp;
    }
  };
  
  const canCurrentUserDelete = (comment) => {
    if (!currentUser.value || !comment.author) return false;
    return comment.author.id === currentUser.value.id ||
           userRole.value === 'ADMIN' ||
           userRole.value === 'MANAGER';
  };
  
  const openDeleteConfirmDialog = (comment) => {
    commentToDelete.value = comment;
    deleteError.value = null;
    isDeleteConfirmOpen.value = true;
  };
  
  const closeDeleteConfirmDialog = () => {
    isDeleteConfirmOpen.value = false;
    commentToDelete.value = null;
  };
  
  const confirmDeleteComment = async () => {
    if (!commentToDelete.value) return;
  
    isDeletingComment.value = true;
    deleteError.value = null;
    try {
      await deleteTaskComment(props.taskId, commentToDelete.value.id);
      comments.value = comments.value.filter(c => c.id !== commentToDelete.value.id);
      closeDeleteConfirmDialog();
    } catch (err) {
      console.error("Failed to delete comment:", err);
      deleteError.value = err?.detail || err?.message || "Could not delete comment. Please try again.";
    } finally {
      isDeletingComment.value = false;
    }
  };
  
  
  onMounted(() => {
    loadComments();
  });
  
  watch(() => props.taskId, (newTaskId) => {
    if (newTaskId) {
      loadComments();
      newCommentText.value = '';
      submitError.value = null;
      deleteError.value = null;
    } else {
      comments.value = [];
    }
  });
  </script>
  
  <style lang="scss" scoped>
  .task-comments-container {
    display: flex;
    flex-direction: column;
    min-height: 300px;
  }
  .comments-list-section {
    flex-grow: 1;
    overflow-y: auto;
    max-height: 350px;
  }
  .comment-item {
    align-items: flex-start;
     padding-left: 0 !important;
     padding-right: 0 !important;
  }
  .comment-content-wrapper {
      width: 100%;
  }
  .comment-text {
    line-height: 1.5;
    color: rgba(var(--v-theme-on-surface), 0.87);
  }
  .comment-action-btn {
      opacity: 0.6;
      &:hover {
          opacity: 1;
      }
  }
  .add-comment-section {
    flex-shrink: 0;
    padding-top: 8px;
  }
  .add-comment-btn {
    display: flex;
    margin-left: auto;
  }
  
  :deep(.v-list-item__prepend) {
    align-self: flex-start !important;
  }
  </style>