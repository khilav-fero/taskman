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
                      color="error" 
                      @click="openDeleteConfirmDialog(comment)"
                      density="comfortable"
                      class="ml-auto comment-action-btn"
                  >
                      <v-icon size="small">mdi-delete-outline</v-icon>
                      <v-tooltip activator="parent" location="top">Delete Comment</v-tooltip>
                  </v-btn>
                </div>
                <p class="text-body-4 comment-text" style="white-space: pre-wrap;">
                  <template v-for="(segment, segIndex) in parseCommentTextForMentions(comment.text)" :key="segIndex">
                    <span v-if="segment.type === 'text'">{{ segment.content }}</span>
                    <span v-else-if="segment.type === 'mention'" class="comment-mention">
                      {{ segment.content }}
                    </span>
                  </template>
                </p>
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
          label="Add a comment... (use @username for mentions)"
          variant="outlined"
          rows="3"
          auto-grow
          hide-details="auto"
          density="compact"
          class="mb-2"
          :error-messages="submitError ? [submitError] : []"
          @keydown.enter.ctrl="handleAddComment"
          @keydown.enter.meta="handleAddComment"
        ></v-textarea>
        <div class="d-flex justify-end align-center">
           <span class="text-caption text-medium-emphasis mr-2" v-if="newCommentText">Ctrl/Cmd + Enter to submit</span>
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
  
  const currentUser = inject('currentUser', ref(null)); // Injected from TaskListView or a global provider
  
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
  const currentUserId = computed(() => currentUser.value?.id || null);
  
  
  const MENTION_REGEX = /@([a-zA-Z0-9_.-]+)/g; 
  
  const parseCommentTextForMentions = (text) => {
    if (typeof text !== 'string' || !text) return [{ type: 'text', content: text || '' }];
  
    const segments = [];
    let lastIndex = 0;
    let match;
  
    MENTION_REGEX.lastIndex = 0;
  
    while ((match = MENTION_REGEX.exec(text)) !== null) {
      if (match.index > lastIndex) {
        segments.push({ type: 'text', content: text.substring(lastIndex, match.index) });
      }
      segments.push({ type: 'mention', content: match[0], username: match[1] });
      lastIndex = match.index + match[0].length;
    }
  
    if (lastIndex < text.length) {
      segments.push({ type: 'text', content: text.substring(lastIndex) });
    }
    
    return segments.length > 0 ? segments : [{ type: 'text', content: text }];
  };
  
  const loadComments = async () => {
    if (!props.taskId) {
      comments.value = [];
      return;
    }
    isLoadingComments.value = true;
    fetchError.value = null;
    try {
      const data = await fetchTaskComments(props.taskId);
      const rawComments = Array.isArray(data) ? data : (data.results || []);
      comments.value = rawComments.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
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
      // Fallback for invalid date strings
      return String(timestamp).substring(0, 10);
    }
  };
  
  const canCurrentUserDelete = (comment) => {
    if (!currentUserId.value || !comment.author || comment.author.id === undefined) return false;
    return comment.author.id === currentUserId.value ||
           userRole.value === 'ADMIN' ||
           userRole.value === 'MANAGER';
  };
  
  const openDeleteConfirmDialog = (comment) => {
    commentToDelete.value = comment;
    deleteError.value = null; // Clear previous delete errors
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
  
  watch(() => props.taskId, (newTaskId, oldTaskId) => {
    if (newTaskId && newTaskId !== oldTaskId) {
      loadComments();
      newCommentText.value = ''; // Clear input when task changes
      submitError.value = null;
      deleteError.value = null;
    } else if (!newTaskId) {
      comments.value = []; // Clear comments if no task ID
    }
  });
  </script>
  
  <style lang="scss" scoped>
  .task-comments-container {
    display: flex;
    flex-direction: column;
    min-height: 300px; // Ensure it has some space
  }
  .comments-list-section {
    flex-grow: 1;
    overflow-y: auto;

    max-height: calc(70vh - 120px - 48px - 120px); // Example, adjust as needed
    padding-right: 4px; // For scrollbar
  }
  .comment-item {
    align-items: flex-start;
     padding-left: 0 !important; // Override Vuetify default list padding
     padding-right: 0 !important;
  }
  .comment-content-wrapper {
      width: 100%; // Ensure it takes full width within list item
  }
  .comment-text {
    line-height: 1.5;
    color: rgba(var(--v-theme-on-surface), 0.87); // Standard text color
  }
  .comment-mention {
    font-weight: 600; // Make it slightly bolder
    color: rgb(var(--v-theme-primary)); // Use primary theme color

    cursor: default; // Or 'pointer' if you add click actions
  }
  .comment-action-btn {
      opacity: 0.5; // Make it less prominent until hover
      transition: opacity 0.2s ease-in-out;
      &:hover {
          opacity: 1;
      }
  }
  .add-comment-section {
    flex-shrink: 0; // Prevent this section from shrinking
    padding-top: 12px; // Space above input
    border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
    margin-top: 12px;
  }
  .add-comment-btn {
    // display: flex; // Not needed if using d-flex on parent
    // margin-left: auto; // Not needed if using d-flex on parent
  }
  
  // Ensure prepend avatar aligns to the top with text
  :deep(.v-list-item__prepend) {
    align-self: flex-start !important;
  }
  </style>