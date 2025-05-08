<template>
  <v-container fluid class="pa-4 user-list-view-container">
    <div class="d-flex justify-space-between align-center mb-5 flex-shrink-0">
      <h1 class="text-h5 font-weight-medium header-title">USERS</h1>
    </div>

    <v-card
      :loading="usersLoading || formSubmitting"
      variant="outlined"
      class="d-flex flex-column card-container"
      :color="$vuetify.theme.current.colors.surface"
    >
      <div class="card-header-section flex-shrink-0">
        <v-card-text class="filter-section-padding">
          <v-row dense align="center" justify="space-between" class="filter-row">
            <v-col cols="auto" sm="auto" md="auto" class="d-flex flex-wrap ga-3 filter-controls-left">
              <div class="filter-item">
                <v-select
                    v-model="selectedRolesFilter"
                    :items="availableRolesForFilter"
                    item-title="title"
                    item-value="value"
                    label="Filter by Role"
                    multiple
                    chips
                    clearable
                    closable-chips
                    density="comfortable"
                    variant="outlined"
                    hide-details="auto"
                    color="primary"
                    class="filter-control themed-input"
                    bg-color="surface"
                ></v-select>
              </div>
              <div class="filter-item">
                <v-text-field
                    v-model="searchFilter"
                    label="Search Users"
                    prepend-inner-icon="mdi-magnify"
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    clearable
                    color="primary"
                    class="filter-control themed-input"
                    bg-color="surface"
                ></v-text-field>
              </div>
            </v-col>

            <v-col cols="auto" sm="auto" md="auto" class="add-user-col">
              <v-btn v-if="isAdmin" color="primary" @click="openCreateDialog" prepend-icon="mdi-plus" variant="flat" class="add-user-btn">
                Add User
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>

        <v-alert
          v-if="showListErrorAlert"
          type="error"
          variant="tonal"
          closable
          class="mx-4 my-2 flex-shrink-0"
          density="compact"
          title="Error Loading Users"
          @update:modelValue="clearUsersError"
        >
          {{ usersError }}
        </v-alert>
      </div>

      <div class="table-and-state-wrapper flex-grow-1 d-flex flex-column">
        <template v-if="showTableLayout">
          <v-data-table
            v-if="initialDataLoadedAndHasUsers"
            :headers="dataTableHeaders"
            :items="filteredUserListData"
            :loading="usersLoading"
            :items-per-page="itemsPerPage"
            :sort-by="initialSortBy"
            item-value="id"
            class="user-data-table"
            fixed-header
            height="100%"
            density="comfortable"
            hover
            :no-data-text="noDataText"
          >
            <template v-slot:item.username="{ item }">
              <span class="font-weight-medium data-table-primary-text">{{ item.username }}</span>
            </template>
            <template v-slot:item.email="{ item }">
              <span class="data-table-secondary-text">{{ item.email }}</span>
            </template>
            <template v-slot:item.first_name="{ item }">
              <span class="data-table-secondary-text">{{ item.first_name || '–' }}</span>
            </template>
            <template v-slot:item.last_name="{ item }">
              <span class="data-table-secondary-text">{{ item.last_name || '–' }}</span>
            </template>
            <template v-slot:item.role="{ item }">
              <v-chip v-if="item" :color="getRoleColor(item.profile?.role)" size="small" label variant="flat" class="data-table-chip font-weight-medium text-uppercase">
                {{ item.profile?.role || 'N/A' }}
              </v-chip>
            </template>
            <template v-slot:item.actions="{ item }">
              <div v-if="item" class="text-center action-icons">
                <v-tooltip text="Edit User" location="top">
                  <template v-slot:activator="{ props: tooltip }">
                    <v-btn
                      v-bind="tooltip"
                      v-if="isAdmin"
                      icon="mdi-pencil-outline"
                      size="small"
                      variant="text"
                      color="primary"
                      @click.stop="openEditDialog(item)"
                      :disabled="formSubmitting"
                      class="mr-1"
                      :aria-label="'Edit user ' + item.username"
                    />
                  </template>
                </v-tooltip>
                <v-tooltip text="Delete User" location="top">
                  <template v-slot:activator="{ props: tooltip }">
                    <v-btn
                      v-bind="tooltip"
                      v-if="isAdmin && (injectedCurrentUser && injectedCurrentUser.id !== item.id)"
                      icon="mdi-delete-outline"
                      size="small"
                      variant="text"
                      color="error"
                      @click.stop="openDeleteDialog(item)"
                      :disabled="formSubmitting"
                      :aria-label="'Delete user ' + item.username"
                    />
                  </template>
                </v-tooltip>
              </div>
            </template>
            <template v-slot:loading>
              <v-skeleton-loader type="table-row@10" :color="$vuetify.theme.current.colors.surface"/>
            </template>
              <template v-slot:no-data>
              <div class="text-center pa-6 text-medium-emphasis">
                <v-icon size="48" class="mb-3" color="grey-lighten-1">mdi-account-search-outline</v-icon>
                <div class="text-subtitle-1 data-table-primary-text">
                  <template v-if="hasActiveFilters">No users found matching your filters.</template>
                  <template v-else-if="!initialDataLoadedAndHasUsers">No users exist in the system.</template>
                  <template v-else>No users found.</template>
                </div>
                <p class="text-caption data-table-secondary-text" v-if="!hasActiveFilters && isAdmin">
                    Try adding a new user or adjusting your filters.
                </p>
              </div>
            </template>
          </v-data-table>
          <div v-else class="empty-state-content">
              <v-icon size="64" :color="$vuetify.theme.current.colors.secondary" class="mb-4">mdi-account-group-outline</v-icon>
              <p class="text-h6 font-weight-regular data-table-primary-text">No Users Found</p>
              <p class="text-body-2 data-table-secondary-text">There are no users in the system to display.</p>
              <v-btn v-if="isAdmin" color="primary" @click="openCreateDialog" class="mt-4 add-user-btn">Add New User</v-btn>
          </div>
        </template>

        <div v-else-if="!usersLoading && !showListErrorAlert" class="initializing-placeholder">
          <v-progress-circular indeterminate color="primary" size="40"/>
          <span class="ml-3 data-table-secondary-text">Loading User Data...</span>
        </div>
      </div>
    </v-card>

    <v-dialog v-model="showFormDialog" persistent max-width="550px" @keydown.esc="closeDialog">
      <v-card :loading="formSubmitting" :color="$vuetify.theme.current.colors.surface">
        <v-toolbar color="primary" flat>
            <v-toolbar-title class="text-h6 font-weight-medium">{{ isEditing ? 'Edit User' : 'Create New User' }}</v-toolbar-title>
            <v-spacer/>
            <v-btn icon="mdi-close" @click="closeDialog" variant="text"/>
        </v-toolbar>
        <v-card-text class="pt-6 pb-4 px-6">
          <v-alert
             v-if="formError"
             type="error" variant="tonal" closable density="compact" class="mb-5"
             title="Error"
             @update:modelValue="clearFormError"
          >
             {{ formError }}
          </v-alert>
          <v-form ref="userFormRef" @submit.prevent="saveUser">
              <v-row dense>
                  <v-col cols="12" sm="6">
                     <v-text-field
                        v-model="form.username"
                        label="Username*"
                        variant="outlined" density="comfortable"
                        :rules="[rules.required, rules.username]"
                        required color="primary"
                        prepend-inner-icon="mdi-account-outline"
                     />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="form.email"
                        label="Email*"
                        type="email"
                        variant="outlined" density="comfortable"
                        :rules="[rules.required, rules.email]"
                        required color="primary"
                        prepend-inner-icon="mdi-email-outline"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="form.first_name"
                        label="First Name"
                         variant="outlined" density="comfortable" color="primary"
                         prepend-inner-icon="mdi-account-details-outline"
                     />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="form.last_name"
                        label="Last Name"
                        variant="outlined" density="comfortable" color="primary"
                        prepend-inner-icon="mdi-account-details-outline"
                    />
                   </v-col>
                   <v-col cols="12" sm="6">
                    <v-select
                        v-model="form.role"
                        label="Role*"
                        :items="availableRolesForFilter"
                         item-title="title" item-value="value"
                        variant="outlined" density="comfortable"
                        :rules="[rules.required]"
                        required color="primary"
                        prepend-inner-icon="mdi-account-star-outline"
                    />
                  </v-col>
                  <template v-if="!isEditing">
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="form.password"
                        label="Password*"
                        type="password"
                        variant="outlined" density="comfortable"
                        :rules="[rules.required, rules.password]"
                        required color="primary"
                        autocomplete="new-password"
                        prepend-inner-icon="mdi-lock-outline"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                        <v-text-field
                            v-model="form.passwordConfirm"
                            label="Confirm Password*"
                            type="password"
                            variant="outlined" density="comfortable"
                            :rules="[rules.required, v => v === form.password || 'Passwords do not match']"
                            required color="primary"
                            autocomplete="new-password"
                            prepend-inner-icon="mdi-lock-check-outline"
                        />
                    </v-col>
                  </template>
               </v-row>
          </v-form>
           <small class="text-caption text-disabled mt-1 d-block">* Indicates required field</small>
        </v-card-text>
        <v-divider/>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="closeDialog" :disabled="formSubmitting" class="data-table-secondary-text">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveUser" :loading="formSubmitting" class="add-user-btn font-weight-bold">{{ isEditing ? 'Save Changes' : 'Create User' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showDeleteDialog" persistent max-width="450px" @keydown.esc="closeDeleteDialog">
      <v-card :loading="formSubmitting" :color="$vuetify.theme.current.colors.surface">
         <v-card-title class="text-h5 font-weight-medium d-flex align-center" :style="{ color: $vuetify.theme.current.colors.error }">
            <v-icon start :color="$vuetify.theme.current.colors.error">mdi-alert-circle-outline</v-icon>
            Confirm Deletion
        </v-card-title>
        <v-card-text class="py-4 data-table-primary-text">
            Are you sure you want to permanently delete the user:
            <br/>
            <strong class="text-subtitle-1 my-1 d-block">{{ userToDelete?.username }}</strong> (ID: {{ userToDelete?.id }})?
            <br/>
            <strong :style="{ color: $vuetify.theme.current.colors.error }">This action cannot be undone.</strong>
            <v-alert
                v-if="formError"
                type="error" variant="tonal" closable density="compact" class="mt-4"
                 title="Error"
                @update:modelValue="clearFormError"
             >
                {{ formError }}
             </v-alert>
        </v-card-text>
        <v-card-actions class="pa-3">
          <v-spacer />
          <v-btn variant="text" @click="closeDeleteDialog" :disabled="formSubmitting" class="data-table-secondary-text">Cancel</v-btn>
          <v-btn color="error" variant="flat" @click="confirmDeleteUser" :loading="formSubmitting" class="font-weight-bold">Delete User</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, reactive, inject } from 'vue';
import { fetchAllUsers, createUserApi, updateUserApi, deleteUserApi } from '@/services/userService';
import { roleChoicesForSelect } from '@/lib/choices'; // Assuming this path and content

const injectedCurrentUser = inject('currentUser', ref(null));

const componentReady = ref(false);
const itemsPerPage = ref(10); // Adjusted from 5 for more visibility
const initialSortBy = ref([{ key: 'username', order: 'asc' }]);

const usersList = ref([]);
const usersLoading = ref(false);
const usersError = ref(null);
const formSubmitting = ref(false);
const formError = ref(null);

const showFormDialog = ref(false);
const showDeleteDialog = ref(false);

const isEditing = ref(false);
const userFormRef = ref(null); // Changed from userForm to avoid conflict with reactive form
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

const selectedRolesFilter = ref([]);
const searchFilter = ref('');

const rules = {
  required: value => !!value || 'Required.',
  email: value => /.+@.+\..+/.test(value) || 'E-mail must be valid.',
  username: value => (value && value.length >= 3) || 'Min 3 characters.',
  password: value => (value && value.length >= 8) || 'Min 8 characters.',
};

const dataTableHeaders = ref([
  { title: 'Username', key: 'username', sortable: true, width: '20%' },
  { title: 'Email', key: 'email', sortable: true, minWidth: '180px', width: '25%' },
  { title: 'First Name', key: 'first_name', sortable: true, width: '15%' },
  { title: 'Last Name', key: 'last_name', sortable: true, width: '15%' },
  { title: 'Role', key: 'role', sortable: true, align: 'center', width: '15%' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '10%' }
]);

const availableRolesForFilter = computed(() => {
  return roleChoicesForSelect;
});

const filteredUserListData = computed(() => {
    let users = usersList.value || [];
    if (selectedRolesFilter.value && selectedRolesFilter.value.length > 0) {
        users = users.filter(user => user.profile?.role && selectedRolesFilter.value.includes(user.profile.role));
    }
    const searchTerm = searchFilter.value?.trim().toLowerCase();
    if (searchTerm) {
        users = users.filter(user => {
            const usernameMatch = user.username?.toLowerCase().includes(searchTerm);
            const emailMatch = user.email?.toLowerCase().includes(searchTerm);
            const firstNameMatch = user.first_name?.toLowerCase().includes(searchTerm);
            const lastNameMatch = user.last_name?.toLowerCase().includes(searchTerm);
            return usernameMatch || emailMatch || firstNameMatch || lastNameMatch;
        });
    }
    return users;
});

const showListErrorAlert = computed(() => !!usersError.value && !usersLoading.value);
const showTableLayout = computed(() => componentReady.value && !usersLoading.value && !showListErrorAlert.value);
const initialDataLoadedAndHasUsers = computed(() => (usersList.value || []).length > 0);
const hasActiveFilters = computed(() => (selectedRolesFilter.value && selectedRolesFilter.value.length > 0) || !!searchFilter.value);

const noDataText = computed(() => {
    if (usersLoading.value && !componentReady.value) return 'Loading users...';
    if (!initialDataLoadedAndHasUsers.value && !hasActiveFilters.value) return 'No users exist in the system.';
    if (hasActiveFilters.value) return 'No users match the current filters.';
    if (!initialDataLoadedAndHasUsers.value) return 'No users found.';
    return 'No data available.';
});

const userRole = computed(() => injectedCurrentUser.value?.profile?.role || null);
const isAdmin = computed(() => userRole.value === 'ADMIN');

const getRoleColor = (role) => {
  if (role === 'ADMIN') return 'error';
  if (role === 'MANAGER') return 'warning';
  if (role === 'USER') return 'info';
  return 'secondary';
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
  userFormRef.value?.resetValidation();
};

const openCreateDialog = () => {
  isEditing.value = false;
  resetForm();
  formError.value = null;
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
  form.role = user.profile?.role || null; // Make sure this reflects API structure
  formError.value = null;
  showFormDialog.value = true;
};

const openDeleteDialog = (user) => {
  if (!user) return;
  userToDelete.value = { ...user };
  formError.value = null;
  showDeleteDialog.value = true;
};

const closeDialog = () => {
  showFormDialog.value = false;
  formError.value = null;
};

const closeDeleteDialog = () => {
  showDeleteDialog.value = false;
  userToDelete.value = null;
  formError.value = null;
};

const saveUser = async () => {
  const { valid } = await userFormRef.value?.validate();
  if (!valid) return;

  formSubmitting.value = true;
  formError.value = null;
  let success = false;

  const userData = {
    username: form.username,
    email: form.email,
    first_name: form.first_name || undefined,
    last_name: form.last_name || undefined,
    profile_attributes: { role: form.role }, // Assuming backend expects role under profile_attributes for create/update
  };

  if (!isEditing.value) {
    userData.password = form.password;
  }

  if (!userData.first_name) delete userData.first_name;
  if (!userData.last_name) delete userData.last_name;

  try {
    if (isEditing.value) {
      if (!form.id) return;
      // For update, usually only changed fields are sent.
      // And password is not sent unless changing. Role update might be separate.
      // Here, we send all, assuming API handles partial updates or specific role update.
      // If API expects only 'role' under 'profile_attributes', adjust accordingly for updates.
      await updateUserApi(form.id, userData);
    } else {
      await createUserApi(userData);
    }
    success = true;
  } catch (err) {
    formError.value = err?.detail || err?.message || (Array.isArray(err) ? err.join('; ') : 'Operation failed.');
    console.error(`Failed to ${isEditing.value ? 'update' : 'create'} user:`, err);
  } finally {
    formSubmitting.value = false;
  }

  if (success) {
    closeDialog();
    await loadUsers();
  }
};

const confirmDeleteUser = async () => {
  if (!userToDelete.value?.id) return;
  formSubmitting.value = true;
  formError.value = null;
  try {
    await deleteUserApi(userToDelete.value.id);
    closeDeleteDialog();
    await loadUsers();
  } catch (err) {
    formError.value = err?.detail || err?.message || 'Failed to delete user.';
    console.error("Failed to delete user:", err);
  } finally {
    formSubmitting.value = false;
  }
};

const loadUsers = async () => {
  usersLoading.value = true;
  usersError.value = null;
  try {
    const fetchedUsers = await fetchAllUsers();
    usersList.value = fetchedUsers; // Assuming fetchAllUsers returns the array directly
  } catch (err) {
    usersError.value = err?.detail || err?.message || 'Could not load users.';
    usersList.value = [];
    console.error('UserListView: Could not load users.', err);
  } finally {
    usersLoading.value = false;
    if (!componentReady.value) {
       componentReady.value = true;
    }
  }
};

const clearUsersError = () => {
  usersError.value = null;
};
const clearFormError = () => {
  formError.value = null;
};

onMounted(() => {
  componentReady.value = false;
  loadUsers();
});
</script>

<style lang="scss" scoped>
.user-list-view-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.card-header-section {
  flex-shrink: 0;
  padding: 16px 20px 4px 20px;
}
.card-content-area {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.card-container {
  border: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.12);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  min-height: 0;
  overflow: hidden;
}
.header-title {
  color: rgb(var(--v-theme-on-background));
}
.add-user-btn {
  color: rgb(var(--v-theme-on-primary));
}
.filter-row {
}
.filter-controls-left {
  flex-grow: 1;
  justify-content: flex-start;
}
.add-user-col {
  flex-grow: 0;
  display: flex;
  align-items: center;
}
.filter-item {
  max-width: 260px;
  min-width: 220px;
  flex-basis: 260px;
  flex-grow: 1;
}
.filter-control {
  width: 100%;
  background-color: rgb(var(--v-theme-surface)) !important;
  border-radius: 6px;
  :deep(.v-field) {
      background-color: transparent !important;
      border-radius: 8px;
      transition: box-shadow 0.2s ease-in-out, border-color 0.2s ease-in-out;
      box-shadow: 0 1px 2px 0 rgba(var(--v-theme-on-surface-rgb), 0.03);
  }
  :deep(.v-field__outline) {
    color: rgba(var(--v-theme-on-surface-rgb), 0.30) !important;
    border-width: 1px;
    opacity: 1 !important;
    transition: border-color 0.2s ease-in-out;
  }
   &:hover :deep(.v-field__outline) {
      color: rgba(var(--v-theme-on-surface-rgb), 0.55) !important;
   }
   &.v-input--is-focused :deep(.v-field__outline){
       border-color: rgb(var(--v-theme-primary)) !important;
       border-width: 1px !important;
       box-shadow: 0 0 0 2.5px rgba(var(--v-theme-primary-rgb), 0.2);
   }
   &.v-input--is-focused :deep(.v-field) {
      box-shadow: 0 1px 3px 0 rgba(var(--v-theme-on-surface-rgb), 0.06);
   }
  :deep(.v-label.v-field-label) {
    color: rgba(var(--v-theme-on-surface-rgb), 0.68) !important;
    opacity: 1;
    font-weight: 400;
  }
   :deep(.v-field--active .v-label.v-field-label) {
        color: rgb(var(--v-theme-primary)) !important;
        font-weight: 500;
    }
  :deep(input), :deep(.v-select__selection-text) {
    color: rgb(var(--v-theme-on-surface)) !important;
    font-weight: 400;
  }
   :deep(.v-select__selection .v-chip) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.15) !important;
    color: rgb(var(--v-theme-primary)) !important;
    font-weight: 500;
    height: 28px;
    .v-icon {
        color: rgb(var(--v-theme-primary)) !important;
        font-size: 1rem;
    }
  }
   :deep(.v-field__input::placeholder){
       color: rgba(var(--v-theme-on-surface-rgb), 0.45) !important;
       opacity: 1;
       font-weight: 400;
   }
    :deep(.v-field__prepend-inner .v-icon){
        color: rgba(var(--v-theme-on-surface-rgb), 0.55) !important;
    }
}
.user-data-table {
  color: rgb(var(--v-theme-on-surface));
  :deep(.v-table__wrapper) {
    overflow-y: auto;
    height: 100%;
  }
  :deep(thead th) {
    position: sticky;
    top: 0;
    background-color: rgba(var(--v-theme-surface-rgb), 0.97) !important;
    backdrop-filter: blur(4px);
    z-index: 10;
    border-bottom: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.15) !important;
    color: rgba(var(--v-theme-on-surface-rgb), 0.8) !important;
    font-weight: 500 !important;
    font-size: 0.875rem;
  }
  :deep(tbody tr) {
      &:hover {
          background-color: rgba(var(--v-theme-primary-rgb), 0.07) !important;
      }
  }
  :deep(.v-data-table__td) {
      border-bottom: thin solid rgba(var(--v-theme-on-surface-rgb), 0.08) !important;
      padding-top: 10px !important;
      padding-bottom: 10px !important;
      font-size: 0.875rem;
  }
   :deep(.v-data-table-footer) {
      flex-shrink: 0;
      border-top: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.15) !important;
      color: rgba(var(--v-theme-on-surface-rgb), 0.7) !important;
  }
  .data-table-primary-text {
      color: rgb(var(--v-theme-on-surface));
      line-height: 1.4;
  }
  .data-table-secondary-text {
      color: rgba(var(--v-theme-on-surface-rgb), 0.75);
      line-height: 1.4;
  }
  .data-table-chip {
      color: rgb(var(--v-theme-on-primary)) !important;
  }
  .action-icons .v-btn {
      color: rgba(var(--v-theme-on-surface-rgb), 0.65);
      &:hover {
          color: rgb(var(--v-theme-primary));
      }
  }
   .action-icons .v-btn[color="primary"] {
      &:hover {
           color: rgb(var(--v-theme-primary-darken-1)) !important;
        }
     }
  .action-icons .v-btn[color="error"] {
     &:hover {
       color: rgb(var(--v-theme-error)) !important;
     }
  }
}
.empty-state-content,
.initializing-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 32px;
  flex-grow: 1;
  color: rgb(var(--v-theme-on-surface));
}
.empty-state-content .text-h6, .empty-state-content .text-body-2 {
   color: rgba(var(--v-theme-on-surface-rgb), 0.8);
}
.initializing-placeholder .text-medium-emphasis {
   color: rgba(var(--v-theme-on-surface-rgb), 0.7) !important;
}
:deep(.v-dialog .v-toolbar-title) {
    color: rgb(var(--v-theme-on-primary));
}
:deep(.v-dialog .v-card-actions .v-btn.add-user-btn) {
    color: rgb(var(--v-theme-on-primary));
}
:deep(.v-dialog .v-card-actions .v-btn.data-table-secondary-text) {
    color: rgba(var(--v-theme-on-surface-rgb), 0.75);
    &:hover {
      color: rgb(var(--v-theme-on-surface));
    }
}
:deep(.v-dialog small.text-disabled) {
    color: rgba(var(--v-theme-on-surface-rgb), 0.6) !important;
}
</style>