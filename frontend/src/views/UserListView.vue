<template>
  <v-container fluid class="pa-4 user-list-view-container d-flex flex-column">
    <div class="d-flex justify-space-between align-center mb-4 flex-shrink-0">
      <h1 class="text-h5">User Management</h1>
    </div>

    <v-card
      :loading="usersStore.getUsersLoading"
      variant="outlined"
      class="flex-grow-1 d-flex flex-column card-container"
    >
      <!-- CHECK, might not be properly reactive -->
      <v-alert
        v-if="usersStore.getUsersError"
        type="error"
        variant="tonal"
        closable
        class="ma-2 flex-shrink-0"
        title="Error Loading Users"
      >
        {{ usersStore.getUsersError }}
      </v-alert>

      <v-data-table
        v-if="showTable"
        :headers="dataTableHeaders"
        :items="userListData"
        :items-per-page="15"
        :sort-by="[{ key: 'username', order: 'asc' }]"
        class="flex-grow-1 user-data-table"
        fixed-header
        height="100%"
        density="comfortable"
        hover
        no-data-text="No users to display"
      >
        <template v-slot:item.role="{ item }">
          <v-chip :color="getRoleColor(item.role)" size="small" label variant="flat">
            {{ item.role || 'USER' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <div class="text-center">
            <v-btn
              icon="mdi-account-edit"
              size="small"
              variant="text"
              color="primary"
              @click.stop="() => {}"  
              class="mr-1"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click.stop="() => {}"
            />
          </div>
        </template>

        <!-- possible logical errors, never clears -->
        <template v-slot:loading>
          <v-skeleton-loader type="table-row@4" />
        </template>
      </v-data-table>

      <div v-else-if="false" class="empty-state-content">
        <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-account-group-outline</v-icon>
        <p class="text-h6 font-weight-regular text-medium-emphasis">No Users Found</p>
        <p class="text-body-2 text-disabled">Try refreshing or checking back later.</p>
      </div>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUsersStore } from '@/store/users';

const usersStore = useUsersStore();

const componentReady = ref(false);

const dataTableHeaders = [
  { title: 'ID', key: 'id', sortable: true, width: '80px' },
  { title: 'Username', key: 'username', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Role', key: 'role', sortable: true, align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '100px' }
];

// mock of real user data 
const userListData = ref([
  { id: 1, username: 'alice', email: 'alice@example.com', role: 'ADMIN' },
  { id: 2, username: 'bob', email: 'bob@example.com', role: 'USER' }
]);

const showTable = computed(() =>
  componentReady.value &&
  !usersStore.getUsersLoading &&
  Array.isArray(userListData.value) &&
  userListData.value.length > 0
);

const getRoleColor = (role) => {
  switch (role) {
    case 'ADMIN':
      return 'primary';
    case 'USER':
      return 'secondary';
    default:
      return 'grey';
  }
};

onMounted(() => {
  componentReady.value = true;
});
</script>

<style lang="scss" scoped>
.user-list-view-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.card-container {
  overflow: hidden;
  background-color: #fff;
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
    background-color: white;
    z-index: 1;
  }
}
</style>