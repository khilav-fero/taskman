<template>
    <div class="task-collaborators-section">
      <div class="d-flex justify-space-between align-center mb-2">
        <h4 class="text-subtitle-1 font-weight-medium">Collaborators</h4>
        <v-btn
          v-if="canManage"
          color="primary"
          variant="tonal"
          size="small"
          @click="openAddDialog"
          prepend-icon="mdi-account-plus-outline"
        >
          Add
        </v-btn>
      </div>
  
      <v-alert v-if="error" type="error" density="compact" variant="tonal" class="mb-3">
        {{ error }}
      </v-alert>
  
      <div v-if="displayedCollaborators.length > 0" class="collaborators-list">
        <v-chip
          v-for="collaborator in displayedCollaborators"
          :key="collaborator.id"
          class="ma-1 collaborator-chip"
          color="secondary"
          variant="outlined"
          label
          :closable="canManage"
          @click:close="handleRemoveCollaborator(collaborator.id)"
          :loading="isRemovingCollaboratorId === collaborator.id"
          :disabled="isRemovingCollaboratorId === collaborator.id"
        >
          <v-avatar start size="20" class="mr-1">
            <v-img
              :src="collaborator.profile?.avatar_url || `https://ui-avatars.com/api/?name=${collaborator.username?.substring(0,2)}&background=secondary&color=white&size=20`"
              :alt="collaborator.username"
            ></v-img>
          </v-avatar>
          {{ collaborator.username }}
        </v-chip>
      </div>
      <p v-else class="text-body-2 text-medium-emphasis">No collaborators on this task yet.</p>
  
      <v-dialog v-model="showAddCollaboratorDialog" max-width="500px" persistent scrollable>
        <v-card>
          <v-card-title class="text-h6">Add Collaborator</v-card-title>
          <v-divider></v-divider>
          <v-card-text style="min-height: 150px;">
            <v-autocomplete
              v-model="selectedUserToAdd"
              v-model:search="userSearchText"
              :items="potentialCollaborators"
              item-title="username"
              item-value="id"
              label="Search and select user"
              variant="outlined"
              density="compact"
              return-object
              clearable
              no-filter
              :loading="isLoadingUsers"
              hide-details="auto"
              class="mb-3"
              placeholder="Start typing to search users..."
            >
              <template v-slot:item="{ props: itemProps, item }">
                <v-list-item
                  v-bind="itemProps"
                  :prepend-avatar="item.raw.profile?.avatar_url || `https://ui-avatars.com/api/?name=${item.raw.username?.substring(0,2)}&background=primary&color=white&size=32`"
                  :title="item.raw.username"
                  :subtitle="item.raw.email"
                ></v-list-item>
              </template>
               <template v-slot:no-data>
                  <v-list-item v-if="userSearchText && !isLoadingUsers">
                      <v-list-item-title>No users found matching "{{ userSearchText }}"</v-list-item-title>
                  </v-list-item>
                   <v-list-item v-else-if="!userSearchText && !isLoadingUsers">
                      <v-list-item-title>Start typing a username or email to search</v-list-item-title>
                  </v-list-item>
              </template>
            </v-autocomplete>
            <v-alert v-if="addCollaboratorError" type="error" density="compact" variant="tonal">
              {{ addCollaboratorError }}
            </v-alert>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="closeAddDialog" :disabled="isAddingCollaborator">Cancel</v-btn>
            <v-btn
              color="primary"
              variant="flat"
              @click="confirmAddCollaborator"
              :disabled="!selectedUserToAdd || isAddingCollaborator"
              :loading="isAddingCollaborator"
            >
              Add Collaborator
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, watch, computed } from 'vue';
  import { fetchUsers, addCollaborator, removeCollaborator } from '@/services/collaboratorService';
  import { debounce } from 'lodash';
  
  const props = defineProps({
    taskId: {
      type: [String, Number],
      required: true,
    },
    currentCollaborators: {
      type: Array,
      default: () => [],
    },
    canManage: {
      type: Boolean,
      default: false,
    },
  });
  
  const emit = defineEmits(['collaborator-added', 'collaborator-removed', 'error']);
  
  const displayedCollaborators = ref([]);
  const showAddCollaboratorDialog = ref(false);
  const userSearchText = ref('');
  const potentialCollaborators = ref([]);
  const isLoadingUsers = ref(false);
  const selectedUserToAdd = ref(null);
  const isAddingCollaborator = ref(false);
  const addCollaboratorError = ref(null);
  const isRemovingCollaboratorId = ref(null);
  const error = ref(null);
  
  const alreadyCollaboratorIds = computed(() => {
    return displayedCollaborators.value.map(c => c.id);
  });
  
  watch(
    () => props.currentCollaborators,
    (newVal) => {
      displayedCollaborators.value = [...(newVal || [])];
    },
    { immediate: true, deep: true }
  );
  
  const openAddDialog = () => {
    selectedUserToAdd.value = null;
    userSearchText.value = '';
    potentialCollaborators.value = [];
    addCollaboratorError.value = null;
    showAddCollaboratorDialog.value = true;
  };
  
  const closeAddDialog = () => {
    showAddCollaboratorDialog.value = false;
  };
  
  const debouncedSearchUsers = debounce(async (searchText) => {
    if (!searchText || searchText.length < 2) {
      potentialCollaborators.value = [];
      return;
    }
    isLoadingUsers.value = true;
    addCollaboratorError.value = null;
    try {
      const data = await fetchUsers({ search: searchText, page_size: 10 });
      potentialCollaborators.value = (data.results || []).filter(
          user => !alreadyCollaboratorIds.value.includes(user.id)
      );
    } catch (err) {
      console.error("Failed to search users:", err);
      addCollaboratorError.value = "Failed to fetch users.";
      potentialCollaborators.value = [];
    } finally {
      isLoadingUsers.value = false;
    }
  }, 550);
  
  watch(userSearchText, (newVal) => {
    if (selectedUserToAdd.value && newVal !== selectedUserToAdd.value.username) {
      selectedUserToAdd.value = null;
    }
    debouncedSearchUsers(newVal);
  });
  
  const confirmAddCollaborator = async () => {
    if (!selectedUserToAdd.value || !selectedUserToAdd.value.id) return;
  
    if (alreadyCollaboratorIds.value.includes(selectedUserToAdd.value.id)) {
        addCollaboratorError.value = `${selectedUserToAdd.value.username} is already a collaborator.`;
        return;
    }
  
    isAddingCollaborator.value = true;
    addCollaboratorError.value = null;
    try {
      await addCollaborator(props.taskId, selectedUserToAdd.value.id);
      displayedCollaborators.value.push(selectedUserToAdd.value);
      emit('collaborator-added', selectedUserToAdd.value);
      closeAddDialog();
    } catch (err) {
      console.error("Failed to add collaborator:", err);
      addCollaboratorError.value = err?.detail || err?.status || err?.warning || "Could not add collaborator.";
      if (err?.warning) {
          const alreadyAddedUser = potentialCollaborators.value.find(u => u.id === selectedUserToAdd.value.id);
          if (alreadyAddedUser && !alreadyCollaboratorIds.value.includes(alreadyAddedUser.id)) {
              displayedCollaborators.value.push(alreadyAddedUser);
          }
      }
    } finally {
      isAddingCollaborator.value = false;
    }
  };
  
  const handleRemoveCollaborator = async (userId) => {
    isRemovingCollaboratorId.value = userId;
    error.value = null;
    try {
      await removeCollaborator(props.taskId, userId);
      displayedCollaborators.value = displayedCollaborators.value.filter(c => c.id !== userId);
      emit('collaborator-removed', userId);
    } catch (err) {
      console.error("Failed to remove collaborator:", err);
      error.value = err?.detail || err?.error || "Could not remove collaborator.";
      emit('error', error.value);
    } finally {
      isRemovingCollaboratorId.value = null;
    }
  };
  
  </script>
  
  <style lang="scss" scoped>
  .task-collaborators-section {
    /* Add any specific container styling if needed */
  }
  .collaborators-list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  .collaborator-chip {
    cursor: default;
    :deep(.v-chip__close) {
      font-size: 1rem;
      margin-inline-start: 2px;
    }
  }
  </style>