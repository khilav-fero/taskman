<template>
  <v-container fluid class="pa-md-6 pa-4 user-list-view-container">
    <div class="d-flex justify-space-between align-center mb-6 flex-shrink-0">
      <h1 class="text-h4 font-weight-medium header-title">USERS</h1>
    </div>

    <v-card
      variant="flat"
      class="d-flex flex-column card-container"
      :color="$vuetify.theme.current.colors.surface"
      rounded="lg"
    >
      <div class="card-header-section flex-shrink-0">
        <v-card-text class="filter-section-padding">
          <v-row dense align="center" class="filter-row">
            <v-col cols="12" md="auto" class="d-flex flex-column flex-sm-row flex-wrap ga-sm-4 ga-3 filter-controls-left">
              <div class="filter-item">
                <v-select
                    v-model="selectedRolesFilter"
                    :items="availableRolesForFilter"
                    item-title="title"
                    item-value="value"
                    label="Filter by Role(s)"
                    multiple
                    chips
                    clearable
                    closable-chips
                    density="comfortable"
                    variant="outlined"
                    hide-details="auto"
                    color="primary"
                    class="filter-control"
                    bg-color="transparent"
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
                    class="filter-control"
                    bg-color="transparent"
                ></v-text-field>
              </div>
            </v-col>

            <v-col cols="12" md="auto" class="add-user-col mt-3 mt-md-0">
              <v-btn v-if="isAdmin" color="primary" @click="openCreateDialog" prepend-icon="mdi-plus" variant="flat" class="add-user-btn" block-sm-and-down>
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
          class="mx-4 mb-4 flex-shrink-0"
          density="compact"
          border="start"
          elevation="2"
          prominent
          icon="mdi-alert-circle-outline"
          :title="usersError ? 'Error Loading Users' : undefined"
          @update:modelValue="clearUsersError"
        >
          {{ usersError }}
        </v-alert>
      </div>

      <div class="table-and-state-wrapper flex-grow-1 d-flex flex-column">
        <template v-if="showTableLayout">
          <v-data-table-server
            v-if="initialDataLoaded"
            :headers="dataTableHeaders"
            :items="usersList"
            :items-length="totalUsers"
            :loading="usersLoading"
            v-model:sort-by="sortBy"
            :items-per-page="itemsPerPage"
            @update:options="handleOptionsUpdate"
            item-value="id"
            class="user-data-table"
            fixed-header
            height="100%"
            density="comfortable"
            hover
            :no-data-text="noDataText"
            hide-default-footer
          >
            <template v-slot:item.username="{ item }">
              <div class="d-flex align-center py-1">
                <span class="font-weight-medium data-table-text-primary">{{ item.username }}</span>
              </div>
            </template>
            <template v-slot:item.email="{ item }">
              <span class="data-table-text-secondary">{{ item.email }}</span>
            </template>
            <template v-slot:item.first_name="{ item }">
              <span class="data-table-text-secondary">{{ item.first_name || '–' }}</span>
            </template>
            <template v-slot:item.last_name="{ item }">
              <span class="data-table-text-secondary">{{ item.last_name || '–' }}</span>
            </template>
            <template v-slot:item.role="{ item }">
              <v-chip v-if="item.profile" :color="getRoleColor(item.profile.role)" size="small" label variant="flat" class="data-table-chip text-uppercase">
                {{ item.profile.role || 'N/A' }}
              </v-chip>
               <span v-else class="data-table-text-secondary">N/A</span>
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
                      :disabled="usersLoading"
                      class="mx-1"
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
                      :disabled="usersLoading"
                      :aria-label="'Delete user ' + item.username"
                    />
                  </template>
                </v-tooltip>
              </div>
            </template>
            <template v-slot:loading>
              <v-skeleton-loader type="table-row@10" :color="$vuetify.theme.current.colors.background"/>
            </template>
            <template v-slot:no-data>
              <div class="state-content-message">
                <v-icon size="56" class="mb-3" color="grey-lighten-1">mdi-account-search-outline</v-icon>
                <div class="text-subtitle-1 font-weight-medium">
                  <template v-if="hasActiveFilters && !usersLoading">No users found matching your criteria.</template>
                  <template v-else-if="!initialDataLoaded && !usersLoading && !hasActiveFilters">No users exist in the system.</template>
                  <template v-else-if="usersLoading">Loading users...</template>
                  <template v-else>No users found.</template>
                </div>
                <p class="text-body-2 text-medium-emphasis mt-1" v-if="!hasActiveFilters && isAdmin && !initialDataLoaded && !usersLoading">
                    Try adding a new user to get started.
                </p>
              </div>
            </template>
            <template v-slot:bottom>
              <div class="table-footer-pagination d-flex justify-space-between align-center pa-2" v-if="totalUsers > 0">
                <div class="d-none d-sm-flex align-center text-caption text-medium-emphasis">
                  Rows per page:
                  <v-select
                    v-model="itemsPerPage"
                    :items="itemsPerPageOptions"
                    density="compact"
                    variant="plain"
                    hide-details
                    class="ml-2 items-per-page-select"
                    style="max-width: 80px;"
                  ></v-select>
                </div>
                <v-spacer class="d-sm-none"></v-spacer>
                <v-pagination
                  v-model="currentPageForUI"
                  :length="totalPages"
                  density="comfortable"
                  total-visible="5"
                  active-color="primary"
                  class="table-pagination-control"
                ></v-pagination>
              </div>
            </template>
          </v-data-table-server>
          <div v-else class="state-content-message">
              <v-icon size="64" :color="$vuetify.theme.current.colors.primary" class="mb-4">mdi-account-group-outline</v-icon>
              <p class="text-h6 font-weight-regular">No Users Found</p>
              <p class="text-body-2 text-medium-emphasis mt-1">There are no users in the system to display.</p>
              <v-btn v-if="isAdmin" color="primary" @click="openCreateDialog" class="mt-6" variant="flat">Add New User</v-btn>
          </div>
        </template>
        <div v-else-if="usersLoading && !componentReady" class="state-content-message">
          <v-progress-circular indeterminate color="primary" size="48"/>
          <p class="text-body-1 text-medium-emphasis mt-4">Loading User Data...</p>
        </div>
        <div v-else-if="showListErrorAlert" class="state-content-message">
            <v-icon size="64" color="error" class="mb-4">mdi-alert-circle-outline</v-icon>
            <p class="text-h6 font-weight-medium">Error Loading Data</p>
            <p class="text-body-2 text-medium-emphasis mt-1">{{ usersError }}</p>
            <v-btn color="primary" @click="loadUsers()" class="mt-6" variant="tonal">Try Again</v-btn>
        </div>
      </div>
    </v-card>

    <UserFormDialog
      v-if="showUserFormDialog"
      v-model="showUserFormDialog"
      :user-id-to-edit="editingUserId"
      @saved="handleUserSaved"
    />

    <UserDeleteConfirmationDialog
      v-if="showUserDeleteDialog"
      v-model="showUserDeleteDialog"
      :user-to-delete="userForDeletion"
      @confirmed="handleUserDeleted"
      @error="handleDeleteError"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, inject, watch } from 'vue';
import { fetchAllUsers } from '@/services/userService';
import { roleChoicesForSelect } from '@/lib/choices';
import UserFormDialog from './components/UserFormDialog.vue';
import UserDeleteConfirmationDialog from './components/UserDeleteConfirmationDialog.vue';

const injectedCurrentUser = inject('currentUser', ref(null));

const componentReady = ref(false);
const usersList = ref([]);
const usersLoading = ref(false);
const usersError = ref(null);
const totalUsers = ref(0);

const itemsPerPage = ref(10);
const itemsPerPageOptions = ref([5, 10, 15, 25, 50, 100]);
const currentOffset = ref(0);
const sortBy = ref([{ key: 'username', order: 'asc' }]);
const currentPageForUI = ref(1);

const showUserFormDialog = ref(false);
const editingUserId = ref(null);

const showUserDeleteDialog = ref(false);
const userForDeletion = ref(null);

const selectedRolesFilter = ref([]);
const searchFilter = ref('');

const dataTableHeaders = ref([
  { title: 'Username', key: 'username', sortable: true, width: '20%' },
  { title: 'Email', key: 'email', sortable: true, minWidth: '180px', width: '25%' },
  { title: 'First Name', key: 'first_name', sortable: true, width: '15%' },
  { title: 'Last Name', key: 'last_name', sortable: true, width: '15%' },
  { title: 'Role', key: 'role', sortable: true, align: 'center', width: '15%' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '10%' }
]);

const availableRolesForFilter = computed(() => roleChoicesForSelect);

const totalPages = computed(() => {
  if (totalUsers.value === 0 || itemsPerPage.value <= 0) return 1;
  return Math.ceil(totalUsers.value / itemsPerPage.value);
});

const showListErrorAlert = computed(() => !!usersError.value && !usersLoading.value);
const showTableLayout = computed(() => componentReady.value && !showListErrorAlert.value);
const initialDataLoaded = computed(() => componentReady.value && (usersList.value.length > 0 || (totalUsers.value === 0 && !usersLoading.value)));
const hasActiveFilters = computed(() => (selectedRolesFilter.value && selectedRolesFilter.value.length > 0) || !!searchFilter.value);

const noDataText = computed(() => {
    if (usersLoading.value && !componentReady.value) return 'Loading users...';
    if (usersLoading.value) return 'Fetching data...';
    if (hasActiveFilters.value) return 'No users found matching your criteria.';
    if (initialDataLoaded.value && usersList.value.length === 0 && !hasActiveFilters.value) return 'No users exist in the system.';
    return 'No data available';
});

const userRole = computed(() => injectedCurrentUser.value?.profile?.role || null);
const isAdmin = computed(() => userRole.value === 'ADMIN');

const getRoleColor = (role) => {
  if (role === 'ADMIN') return 'error';
  if (role === 'MANAGER') return 'warning';
  if (role === 'USER' || role === 'TEAM_MEMBER') return 'info';
  return 'secondary';
};

let initialLoadDone = false;
let searchDebounceTimer = null;

async function loadUsers() {
  usersLoading.value = true;
  usersError.value = null;
  try {
    const params = new URLSearchParams();
    params.append('limit', itemsPerPage.value.toString());
    params.append('offset', currentOffset.value.toString());

    if (selectedRolesFilter.value && selectedRolesFilter.value.length > 0) {
      selectedRolesFilter.value.forEach(role => {
        params.append('profile__role', role);
      });
    }

    if (searchFilter.value) {
      params.append('search', searchFilter.value);
    }

    if (sortBy.value && sortBy.value.length > 0) {
      const sortItem = sortBy.value[0];
      let orderingKey = sortItem.key;
      if (orderingKey === 'role') {
        orderingKey = 'profile__role';
      }
      const sortOrder = sortItem.order === 'desc' ? '-' : '';
      params.append('ordering', `${sortOrder}${orderingKey}`);
    }

    const response = await fetchAllUsers(params);
    usersList.value = response.results;
    totalUsers.value = response.count;

    if (!componentReady.value) {
        componentReady.value = true;
    }
    initialLoadDone = true;

  } catch (err) {
    let errorMessage = 'Could not load users.';
    if (err?.detail) errorMessage = err.detail;
    else if (typeof err === 'string') errorMessage = err;
    else if (err?.message) errorMessage = err.message;
    usersError.value = errorMessage;
    usersList.value = [];
    totalUsers.value = 0;
    if (!componentReady.value) {
        componentReady.value = true;
    }
    console.error('UserListView: Could not load users.', err);
  } finally {
    usersLoading.value = false;
  }
}

function handleOptionsUpdate(options) {
  const newPage = options.page || currentPageForUI.value;
  const newItemsPerPage = options.itemsPerPage || itemsPerPage.value;
  const newSortBy = options.sortBy || sortBy.value;

  let needsLoad = false;

  if (newItemsPerPage !== itemsPerPage.value) {
    itemsPerPage.value = newItemsPerPage;
    currentOffset.value = 0;
    currentPageForUI.value = 1;
    needsLoad = true;
  }

  if (newPage !== currentPageForUI.value) {
      currentPageForUI.value = newPage;
      currentOffset.value = (newPage - 1) * itemsPerPage.value;
      needsLoad = true;
  }
  
  if (JSON.stringify(newSortBy) !== JSON.stringify(sortBy.value)) {
    sortBy.value = newSortBy;
    currentOffset.value = 0;
    currentPageForUI.value = 1;
    needsLoad = true;
  }

  if (needsLoad && initialLoadDone) {
    loadUsers();
  }
}


watch(selectedRolesFilter, () => {
  currentOffset.value = 0;
  currentPageForUI.value = 1;
  loadUsers();
}, { deep: true });


watch(searchFilter, () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    currentOffset.value = 0;
    currentPageForUI.value = 1;
    loadUsers();
  }, 400);
});

watch(currentPageForUI, (newPage) => {
    const newOffset = (newPage - 1) * itemsPerPage.value;
    if (newOffset !== currentOffset.value && initialLoadDone) {
        currentOffset.value = newOffset;
        loadUsers();
    }
});

watch(itemsPerPage, (newItemsPerPage) => {
    currentOffset.value = 0;
    currentPageForUI.value = 1;
    if (initialLoadDone) {
        loadUsers();
    }
});


const openCreateDialog = () => {
  editingUserId.value = null;
  showUserFormDialog.value = true;
};

const openEditDialog = (user) => {
  if (!user) return;
  editingUserId.value = user.id;
  showUserFormDialog.value = true;
};

const openDeleteDialog = (user) => {
  if (!user) return;
  userForDeletion.value = { ...user };
  showUserDeleteDialog.value = true;
};

const handleUserSaved = () => {
  editingUserId.value = null;
  loadUsers();
};

const handleUserDeleted = () => {
  userForDeletion.value = null;
  const newTotalPages = Math.ceil((totalUsers.value -1) / itemsPerPage.value);
  if (currentPageForUI.value > newTotalPages && newTotalPages > 0) {
      currentPageForUI.value = newTotalPages;
      currentOffset.value = (newTotalPages - 1) * itemsPerPage.value;
  }
  loadUsers();
};

const handleDeleteError = (errorMessage) => {
  console.error("Delete operation failed (caught by parent):", errorMessage);
  usersError.value = errorMessage;
};

const clearUsersError = () => {
  usersError.value = null;
};

onMounted(() => {
  initialLoadDone = false;
  componentReady.value = false;
  currentOffset.value = (currentPageForUI.value - 1) * itemsPerPage.value;
  loadUsers();
});
</script>

<style lang="scss" scoped>
.user-list-view-container {
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
  padding: 12px 0px 0px 0px;
}

.filter-section-padding {
  padding: 12px 20px 16px 20px !important;
}

.filter-controls-left {
  flex-grow: 1;
}

.add-user-col {
  flex-grow: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.add-user-btn {
  color: rgb(var(--v-theme-on-primary));
  font-weight: 500;
}
@media (max-width: 600px) {
  .add-user-btn {
    width: 100%;
  }
}

.filter-item {
  max-width: 280px;
  min-width: 200px;
  flex-basis: 260px;
  flex-grow: 1;
}

.filter-control {
  :deep(.v-field) {
    background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
    border-radius: var(--v-border-radius-lg);
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
    box-shadow: 0 0 0 3px rgba(var(--v-theme-primary-rgb), 0.12);
  }
  :deep(.v-label.v-field-label) {
    color: rgba(var(--v-theme-on-surface), 0.65) !important;
    font-weight: 400;
  }
  :deep(.v-field--active .v-label.v-field-label) {
    color: rgb(var(--v-theme-primary)) !important;
  }
  :deep(input), :deep(.v-select__selection-text) {
    color: rgb(var(--v-theme-on-surface)) !important;
  }
  :deep(.v-select__selection .v-chip) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.1) !important;
    color: rgb(var(--v-theme-primary)) !important;
    font-weight: 500;
    height: 26px;
    .v-icon {
      color: rgb(var(--v-theme-primary)) !important;
      font-size: 0.9rem;
    }
  }
  :deep(.v-field__prepend-inner .v-icon) {
    color: rgba(var(--v-theme-on-surface), 0.5) !important;
  }
}

.table-and-state-wrapper {
  overflow: hidden;
  position: relative;
  flex-grow: 1;
}

.user-data-table {
  color: rgb(var(--v-theme-on-surface));
  border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);

  :deep(.v-table__wrapper) {
    overflow-y: auto;
    height: 100%;
    border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);
  }

  :deep(thead th) {
    position: sticky;
    top: 0;
    background-color: rgb(var(--v-theme-surface)) !important;
    backdrop-filter: blur(6px);
    z-index: 10;
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.1) !important;
    color: rgba(var(--v-theme-on-surface), 0.75) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    height: 48px !important;
  }

  :deep(tbody tr:hover) {
    background-color: rgba(var(--v-theme-primary-rgb), 0.05) !important;
  }

  :deep(.v-data-table__td) {
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08) !important;
    padding: 12px 16px !important;
    font-size: 0.9rem;
    height: 52px !important;
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
  }

  .data-table-chip {
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    padding: 3px 10px;
    height: 26px !important;
    letter-spacing: 0.02em;
    &.text-uppercase {
      letter-spacing: 0.05em;
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
}

.table-footer-pagination {
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  padding: 10px 16px;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 0 0 var(--v-border-radius-lg) var(--v-border-radius-lg);
  min-height: 58px;

  .items-per-page-select :deep(.v-input__control) {
    min-height: 36px !important;
  }
  .items-per-page-select :deep(.v-field__field) {
    height: 36px !important;
  }
  .items-per-page-select :deep(.v-select__selection-text) {
    font-size: 0.875rem;
  }
  .table-pagination-control :deep(.v-pagination__list) {
    justify-content: flex-end;
  }
  .table-pagination-control :deep(.v-btn) {
    margin: 0 2px;
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
}
.state-content-message .text-h6,
.state-content-message .text-subtitle-1 {
   color: rgba(var(--v-theme-on-surface), 0.9);
}
.state-content-message .text-body-1,
.state-content-message .text-body-2 {
   color: rgba(var(--v-theme-on-surface), 0.65);
}
</style>