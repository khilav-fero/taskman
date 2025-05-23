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
  
  <script>
  import { fetchUsers, addCollaborator, removeCollaborator } from '@/services/collaboratorService';
  import { debounce } from 'lodash';
  
  export default {
    name: 'TaskCollaborators', // Assuming component name
    props: {
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
    },
    emits: ['collaborator-added', 'collaborator-removed', 'error'],
    data() {
      return {
        displayedCollaborators: [],
        showAddCollaboratorDialog: false,
        userSearchText: '',
        potentialCollaborators: [],
        isLoadingUsers: false,
        selectedUserToAdd: null,
        isAddingCollaborator: false,
        addCollaboratorError: null,
        isRemovingCollaboratorId: null,
        error: null,
      };
    },
    computed: {
      alreadyCollaboratorIds() {
        return this.displayedCollaborators.map(c => c.id);
      }
    },
    watch: {
      currentCollaborators: {
        handler(newVal) {
          this.displayedCollaborators = [...(newVal || [])];
        },
        immediate: true,
        deep: true
      },
      userSearchText(newVal) {
        if (this.selectedUserToAdd && newVal !== this.selectedUserToAdd.username) {
          this.selectedUserToAdd = null;
        }
        this.debouncedSearchUsers(newVal);
      }
    },
    created() {
      this.debouncedSearchUsers = debounce(async (searchText) => {
        if (!searchText || searchText.length < 2) {
          this.potentialCollaborators = [];
          return;
        }
        this.isLoadingUsers = true;
        this.addCollaboratorError = null;
        try {
          const data = await fetchUsers({ search: searchText, page_size: 10 });
          this.potentialCollaborators = (data.results || []).filter(
              user => !this.alreadyCollaboratorIds.includes(user.id)
          );
        } catch (err) {
          console.error("Failed to search users:", err);
          this.addCollaboratorError = "Failed to fetch users.";
          this.potentialCollaborators = [];
        } finally {
          this.isLoadingUsers = false;
        }
      }, 550);
    },
    methods: {
      openAddDialog() {
        this.selectedUserToAdd = null;
        this.userSearchText = '';
        this.potentialCollaborators = [];
        this.addCollaboratorError = null;
        this.showAddCollaboratorDialog = true;
      },
      closeAddDialog() {
        this.showAddCollaboratorDialog = false;
      },
      async confirmAddCollaborator() {
        if (!this.selectedUserToAdd || !this.selectedUserToAdd.id) return;
  
        if (this.alreadyCollaboratorIds.includes(this.selectedUserToAdd.id)) {
            this.addCollaboratorError = `${this.selectedUserToAdd.username} is already a collaborator.`;
            return;
        }
  
        this.isAddingCollaborator = true;
        this.addCollaboratorError = null;
        try {
          await addCollaborator(this.taskId, this.selectedUserToAdd.id);
          this.displayedCollaborators.push(this.selectedUserToAdd);
          this.$emit('collaborator-added', this.selectedUserToAdd);
          this.closeAddDialog();
        } catch (err) {
          console.error("Failed to add collaborator:", err);
          this.addCollaboratorError = err?.detail || err?.status || err?.warning || "Could not add collaborator.";
          if (err?.warning) {
              const alreadyAddedUser = this.potentialCollaborators.find(u => u.id === this.selectedUserToAdd.id);
              if (alreadyAddedUser && !this.alreadyCollaboratorIds.includes(alreadyAddedUser.id)) {
                  this.displayedCollaborators.push(alreadyAddedUser);
              }
          }
        } finally {
          this.isAddingCollaborator = false;
        }
      },
      async handleRemoveCollaborator(userId) {
        this.isRemovingCollaboratorId = userId;
        this.error = null;
        try {
          await removeCollaborator(this.taskId, userId);
          this.displayedCollaborators = this.displayedCollaborators.filter(c => c.id !== userId);
          this.$emit('collaborator-removed', userId);
        } catch (err) {
          console.error("Failed to remove collaborator:", err);
          this.error = err?.detail || err?.error || "Could not remove collaborator.";
          this.$emit('error', this.error);
        } finally {
          this.isRemovingCollaboratorId = null;
        }
      }
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