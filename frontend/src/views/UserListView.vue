<template>
  <v-container fluid class="pa-4 user-list-view-container d-flex flex-column">
    <div class="d-flex justify-space-between align-center mb-4 flex-shrink-0">
      <h1 class="text-h5">User Management</h1>
      <v-btn v-if="isAdmin" color="primary" @click="openCreateDialog" prepend-icon="mdi-plus">
        Add User
      </v-btn>
    </div>

    <v-card
      :loading="usersStore.getUsersLoading || usersStore.getFormLoading"
      variant="outlined"
      class="flex-grow-1 d-flex flex-column card-container"
    >
      <v-alert
        v-if="showListError"
        type="error"
        variant="tonal"
        closable
        class="ma-2 flex-shrink-0"
        density="compact"
        title="Error Loading Users"
        @update:modelValue="usersStore.clearUsersError()"
      >
        {{ usersStore.getUsersError }}
      </v-alert>

      <v-data-table
        v-if="showTable"
        :headers="dataTableHeaders"
        :items="userListData"
        :loading="usersStore.getUsersLoading"
        :items-per-page="itemsPerPage"
        :sort-by="initialSortBy"
        item-value="id"
        class="flex-grow-1 user-data-table"
        fixed-header
        height="100%"
        density="comfortable"
        hover
        no-data-text="No users found."
      >
        <template v-slot:item.role="{ item }">
          <v-chip v-if="item" :color="getRoleColor(item.profile?.role)" size="small" label variant="flat">
            {{ item.profile?.role || 'N/A' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <div v-if="item" class="text-center">
            <v-tooltip text="Edit User" location="top">
              <template v-slot:activator="{ props: tooltip }">
                <v-btn
                  v-bind="tooltip"
                  v-if="isAdmin"
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  color="primary"
                  @click.stop="openEditDialog(item)"
                  :disabled="usersStore.getFormLoading"
                  class="mr-1"
                  :aria-label="'Edit user ' + item.username"
                />
              </template>
            </v-tooltip>

            <v-tooltip text="Delete User" location="top">
              <template v-slot:activator="{ props: tooltip }">
                <v-btn
                  v-bind="tooltip"
                  v-if="isAdmin && currentUser?.id !== item.id"
                  icon="mdi-delete"
                  size="small"
                  variant="text"
                  color="error"
                  @click.stop="openDeleteDialog(item)"
                  :disabled="usersStore.getFormLoading"
                  :aria-label="'Delete user ' + item.username"
                />
              </template>
            </v-tooltip>
          </div>
        </template>

        <template v-slot:loading>
          <v-skeleton-loader type="table-row@10" />
        </template>
      </v-data-table>

      <div v-else-if="showEmptyState" class="empty-state-content">
        <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-account-group-outline</v-icon>
        <p class="text-h6 font-weight-regular text-medium-emphasis">No Users Found</p>
        <p class="text-body-2 text-disabled">The user list is currently empty.</p>
      </div>

      <div
        v-else-if="!usersStore.getUsersLoading && !showListError"
        class="initializing-placeholder"
      >
        <v-progress-circular indeterminate color="primary" />
        <span class="ml-4 text-medium-emphasis">Loading Users...</span>
      </div>
    </v-card>

    <v-dialog v-model="showFormDialog" persistent max-width="550px" @keydown.esc="closeDialog">
      <v-card :loading="usersStore.getFormLoading">
        <v-card-title>
           <span class="text-h5">{{ isEditing ? 'Edit User' : 'Create New User' }}</span>
        </v-card-title>
        <v-card-text>
          <v-alert
             v-if="usersStore.getFormError"
             type="error" variant="tonal" closable density="compact" class="mb-4"
             title="Error"
             @update:modelValue="usersStore.clearFormError()"
          >
             {{ usersStore.getFormError }}
          </v-alert>
          <v-form ref="userForm" @submit.prevent="saveUser">
              <v-row dense>
                  <v-col cols="12" sm="6">
                     <v-text-field
                        v-model="form.username"
                        label="Username*"
                        variant="outlined" density="compact"
                        :rules="[rules.required, rules.username]"
                        required
                     />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="form.email"
                        label="Email*"
                        type="email"
                        variant="outlined" density="compact"
                        :rules="[rules.required, rules.email]"
                        required
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="form.first_name"
                        label="First Name"
                         variant="outlined" density="compact"
                     />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="form.last_name"
                        label="Last Name"
                        variant="outlined" density="compact"
                    />
                   </v-col>
                   <v-col cols="12" sm="6">
                    <v-select
                        v-model="form.role"
                        label="Role*"
                        :items="roleChoicesForSelect"
                         item-title="title" item-value="value"
                        variant="outlined" density="compact"
                        :rules="[rules.required]"
                        required
                    />
                  </v-col>
                  <template v-if="!isEditing">
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="form.password"
                        label="Password*"
                        type="password"
                        variant="outlined" density="compact"
                        :rules="[rules.required, rules.password]"
                        required
                        autocomplete="new-password"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                        <v-text-field
                            v-model="form.passwordConfirm"
                            label="Confirm Password*"
                            type="password"
                            variant="outlined" density="compact"
                            :rules="[rules.required, v => v === form.password || 'Passwords do not match']"
                            required
                            autocomplete="new-password"
                        />
                    </v-col>
                  </template>
               </v-row>
          </v-form>
           <small class="text-caption text-disabled">* Indicates required field</small>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey-darken-1" variant="text" @click="closeDialog" :disabled="usersStore.getFormLoading">Cancel</v-btn>
          <v-btn color="primary" variant="elevated" @click="saveUser" :loading="usersStore.getFormLoading">{{ isEditing ? 'Save Changes' : 'Create User' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showDeleteDialog" persistent max-width="450px" @keydown.esc="closeDeleteDialog">
      <v-card :loading="usersStore.getFormLoading">
        <v-card-title class="text-h5 error">Confirm Deletion</v-card-title>
        <v-card-text>
            Are you sure you want to permanently delete the user
            <strong>{{ userToDelete?.username }}</strong> (ID: {{ userToDelete?.id }})?
            <br/>
            <strong class="text-error">This action cannot be undone.</strong>
            <v-alert
                v-if="usersStore.getFormError"
                type="error" variant="tonal" closable density="compact" class="mt-4"
                 title="Error"
                @update:modelValue="usersStore.clearFormError()"
             >
                {{ usersStore.getFormError }}
             </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey-darken-1" variant="text" @click="closeDeleteDialog" :disabled="usersStore.getFormLoading">Cancel</v-btn>
          <v-btn color="error" variant="elevated" @click="confirmDeleteUser" :loading="usersStore.getFormLoading">Delete User</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useUsersStore } from '@/store/users';
import { useAuthStore } from '@/store/auth';
import { roleChoicesForSelect } from '@/lib/choices';

const usersStore = useUsersStore();
const authStore = useAuthStore();

const componentReady = ref(false);
const itemsPerPage = ref(15);
const initialSortBy = ref([{ key: 'username', order: 'asc' }]);

const showFormDialog = ref(false);
const showDeleteDialog = ref(false);

const isEditing = ref(false);
const userForm = ref(null);
const form = reactive({
  id: null,
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: null,
  password: '',
  passwordConfirm: ''
});
const userToDelete = ref(null);

const rules = {
  required: value => !!value || 'Required.',
  email: value => /.+@.+\..+/.test(value) || 'E-mail must be valid.',
  username: value => (value && value.length >= 3) || 'Min 3 characters.',
  password: value => (value && value.length >= 8) || 'Min 8 characters.',
};

const dataTableHeaders = ref([
  { title: 'Username', key: 'username', sortable: true },
  { title: 'Email', key: 'email', sortable: true, minWidth: '180px' },
  { title: 'First Name', key: 'first_name', sortable: true, width: '130px' },
  { title: 'Last Name', key: 'last_name', sortable: true, width: '130px' },
  { title: 'Role', key: 'role', sortable: true, align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '120px' }
]);

const userListData = computed(() => usersStore.getUserList || []);
const hasUsers = computed(() => userListData.value.length > 0);
const showListError = computed(() => !!usersStore.getUsersError && !usersStore.getUsersLoading);
const showTable = computed(() =>
  componentReady.value && !usersStore.getUsersLoading && !showListError.value && hasUsers.value
);
const showEmptyState = computed(() =>
  componentReady.value && !usersStore.getUsersLoading && !showListError.value && !hasUsers.value
);
const isAdmin = computed(() => authStore.userRole === 'ADMIN');
const currentUser = computed(() => authStore.getUser);

const getRoleColor = (role) => {
  if (role === 'ADMIN') return 'error';
  if (role === 'MANAGER') return 'warning';
  return 'info';
};

const resetForm = () => {
  form.id = null;
  form.username = '';
  form.email = '';
  form.first_name = '';
  form.last_name = '';
  form.role = null;
  form.password = '';
  form.passwordConfirm = '';
  userForm.value?.resetValidation();
};

const openCreateDialog = () => {
  isEditing.value = false;
  resetForm();
  usersStore.clearFormError();
  showFormDialog.value = true;
};

const openEditDialog = (user) => {
  if (!user) return;
  isEditing.value = true;
  resetForm();
  form.id = user.id;
  form.username = user.username;
  form.email = user.email;
  form.first_name = user.first_name || '';
  form.last_name = user.last_name || '';
  form.role = user.profile?.role || null;
  usersStore.clearFormError();
  showFormDialog.value = true;
};

const openDeleteDialog = (user) => {
  if (!user) return;
  userToDelete.value = { ...user };
  usersStore.clearFormError();
  showDeleteDialog.value = true;
};

const closeDialog = () => {
  showFormDialog.value = false;
  usersStore.clearFormError();
};

const closeDeleteDialog = () => {
  showDeleteDialog.value = false;
  userToDelete.value = null;
  usersStore.clearFormError();
};

const saveUser = async () => {
  const { valid } = await userForm.value?.validate();
  if (!valid) {
      return;
  }

  usersStore.clearFormError();
  let success = false;

  const userData = {
    username: form.username,
    email: form.email,
    first_name: form.first_name || undefined,
    last_name: form.last_name || undefined,
    profile_attributes: { role: form.role },
  };
  if (!isEditing.value) {
    userData.password = form.password;
  }
  if (!userData.first_name) delete userData.first_name;
  if (!userData.last_name) delete userData.last_name;


  try {
    if (isEditing.value) {
      if (!form.id) return;
      success = await usersStore.updateUserAction(form.id, userData);
    } else {
      success = await usersStore.createUserAction(userData);
    }

    if (success) {
      closeDialog();
      await loadUsers();
    }
  } catch (error) {
    console.error(`Failed to ${isEditing.value ? 'update' : 'create'} user:`, error);
  }
};

const confirmDeleteUser = async () => {
  if (!userToDelete.value?.id) return;

  usersStore.clearFormError();
  try {
    const success = await usersStore.deleteUserAction(userToDelete.value.id);
    if (success) {
      closeDeleteDialog();
      await loadUsers();
    }
  } catch (error) {
    console.error("Failed to delete user:", error);
  }
};

const loadUsers = async () => {
  usersStore.clearUsersError();
  try {
    await usersStore.fetchUsersAction();
  } catch (error) {
    console.error('UserListView: Could not load users.', error);
  } finally {
    if (!componentReady.value) {
       componentReady.value = true;
    }
  }
};

onMounted(() => {
  componentReady.value = false;
  loadUsers();
});
</script>

<style lang="scss" scoped>
.user-list-view-container {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}
.card-container {
  overflow: hidden;
}
.user-data-table {
  height: 100%;
  display: flex;
  flex-direction: column;
  :deep(.v-table__wrapper) {
    flex-grow: 1;
    overflow-y: auto;
  }
  :deep(thead th) {
    position: sticky;
    top: 0;
    background-color: rgb(var(--v-theme-surface));
    z-index: 1;
  }
}
.empty-state-content,
.initializing-placeholder {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 32px;
}
</style>