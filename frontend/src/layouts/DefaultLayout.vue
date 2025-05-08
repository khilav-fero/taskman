<template>
    <v-navigation-drawer
      v-if="shouldShowSidebar"
      v-model="drawerVisibleState"
      :rail="rail && lgAndUp"
      :expand-on-hover="rail && lgAndUp"
      :permanent="lgAndUp"
      :temporary="!lgAndUp"
      app
      color="surface"
      class="nav-drawer"
      width="260"
      rail-width="72"
    >
      <v-list-item
        lines="two"
        :prepend-avatar="injectedCurrentUser?.profile?.avatar_url || 'https://via.placeholder.com/40/' + ($vuetify.theme.current.colors.primary.substring(1)) + '/FFFFFF?text=' + (injectedCurrentUser?.username?.[0]?.toUpperCase() || 'U')"
        nav
        class="user-profile-list-item pa-2 mx-1 mt-1"
        min-height="68"
        :title="(!rail || !lgAndUp) ? (injectedCurrentUser?.username || 'User') : undefined"
        :subtitle="(!rail || !lgAndUp) ? (userRole) : undefined"
      >
        <template v-slot:append v-if="lgAndUp && !rail">
          <v-tooltip location="end" text="Collapse Sidebar">
            <template v-slot:activator="{props}">
              <v-btn
                v-bind="props"
                variant="text"
                icon="mdi-chevron-left"
                @click.stop="rail = true"
                size="small"
                class="collapse-btn"
              ></v-btn>
            </template>
          </v-tooltip>
        </template>
      </v-list-item>
  
      <v-divider class="mx-2 my-1"></v-divider>
  
      <v-list density="compact" nav class="pa-1">
        <template v-for="item in navigationItems" :key="item.value">
          <v-list-item
            v-if="shouldShowNavItem(item)"
            :prepend-icon="item.icon"
            :title="item.title"
            :value="item.value"
            :to="{ name: item.routeName }"
            active-class="drawer-list-item--active"
            class="drawer-list-item ma-1"
            link
            rounded="lg"
          >
            <v-tooltip location="end" :text="item.title" :disabled="(!rail && !drawerHovering) || !lgAndUp || (drawerHovering && !rail)">
              <template v-slot:activator="{ props }">
                <div v-bind="props" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></div>
              </template>
            </v-tooltip>
          </v-list-item>
        </template>
      </v-list>
  
      <template v-slot:append>
        <div class="pa-2 drawer-append-logout">
          <v-tooltip location="top" text="Logout" :disabled="!rail || !lgAndUp">
            <template v-slot:activator="{props}">
              <v-btn
                v-bind="props"
                :block="!rail || !lgAndUp"
                :icon="rail && lgAndUp ? 'mdi-logout-variant' : undefined"
                :prepend-icon="!rail || !lgAndUp ? 'mdi-logout-variant' : undefined"
                @click="triggerLogoutRequest"
                color="secondary"
                :variant="rail && lgAndUp ? 'text' : 'tonal'"
                v-if="isUserAuthenticated"
                class="logout-btn"
                :size="rail && lgAndUp ? 'default' : 'default'"
              >
                <span v-if="!rail || !lgAndUp">Logout</span>
              </v-btn>
            </template>
          </v-tooltip>
        </div>
      </template>
    </v-navigation-drawer>
  
    <v-app-bar app color="surface" flat height="64" class="app-bar-border">
      <v-app-bar-nav-icon
        v-if="shouldShowSidebar && !lgAndUp"
        @click.stop="drawerVisibleState = !drawerVisibleState"
      ></v-app-bar-nav-icon>
      <v-btn
        v-else-if="shouldShowSidebar && lgAndUp && rail"
        variant="text"
        icon="mdi-menu"
        @click.stop="rail = false"
        size="small"
        class="expand-from-rail-btn"
      ></v-btn>
      <v-toolbar-title class="app-title d-flex align-center" :class="{'pl-2': shouldShowSidebar && lgAndUp && rail}">
        <v-icon color="primary" class="mr-2 d-none d-sm-inline-block">mdi-checkbox-marked-circle-auto-outline</v-icon>
        Taskman
      </v-toolbar-title>
  
      <v-spacer />
  
      <template v-if="!isUserAuthenticated">
        <v-btn :to="{ name: 'Login' }" class="auth-btn mx-1" variant="text">Login</v-btn>
        <v-btn :to="{ name: 'Register' }" class="auth-btn mx-1" variant="flat" color="primary">Register</v-btn>
      </template>
    </v-app-bar>
  
    <v-main class="main-content-area">
      <router-view v-slot="{ Component, route: currentViewRoute }">
        <transition name="page-fade-slide" mode="out-in">
          <component
            :is="Component"
            :key="currentViewRoute.path"
          />
        </transition>
      </router-view>
    </v-main>
  </template>
  
  <script setup>
  import { ref, computed, watch, inject } from 'vue';
  import { useDisplay } from 'vuetify';
  import { useRoute, useRouter } from 'vue-router';
  
  const { lgAndUp } = useDisplay();
  const route = useRoute();
  const router = useRouter();
  
  const injectedCurrentUser = inject('currentUser');
  const isUserAuthenticated = inject('isAuthenticated'); 
  
  const userRole = computed(() => injectedCurrentUser.value?.profile?.role || null);
  
  const drawerVisibleState = ref(lgAndUp.value);
  const rail = ref(lgAndUp.value);
  const drawerHovering = ref(false);
  
  
  const shouldShowSidebar = computed(() => {
    return isUserAuthenticated.value && !route.meta.hideSidebar;
  });
  
  watch(lgAndUp, (newVal) => {
    if (shouldShowSidebar.value) {
      drawerVisibleState.value = newVal;
      rail.value = newVal;
    } else {
      drawerVisibleState.value = false;
    }
  });
  
  watch(shouldShowSidebar, (newVal) => {
      if (newVal) {
          drawerVisibleState.value = lgAndUp.value;
          rail.value = lgAndUp.value;
      } else {
          drawerVisibleState.value = false;
          rail.value = false;
      }
  }, { immediate: true });
  
  
  const navigationItems = ref([
    { title: 'Tasks', icon: 'mdi-view-list-outline', value: 'tasks', routeName: 'TaskList', requiresAuth: true },
    { title: 'Users', icon: 'mdi-account-group-outline', value: 'users', routeName: 'UserList', requiresAdminOrManager: true, requiresAuth: true },
  ]);
  
  const isAdminOrManager = computed(() => {
    return userRole.value === 'ADMIN' || userRole.value === 'MANAGER';
  });
  
  const shouldShowNavItem = (item) => {
    if (item.requiresAuth && !isUserAuthenticated.value) return false;
    if (item.requiresAdminOrManager && !isAdminOrManager.value) return false;
    return true;
  };
  
  const emit = defineEmits(['logout-request']);
  
  function triggerLogoutRequest() {
    emit('logout-request');
  }
  </script>
  
  <style scoped lang="scss">
  .nav-drawer {
      border-right: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.08) !important;
      transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  
      .v-navigation-drawer__content {
          overflow-x: hidden;
          display: flex;
          flex-direction: column;
      }
      &.v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) {
        .user-profile-list-item .v-list-item-title,
        .user-profile-list-item .v-list-item-subtitle {
          opacity: 0;
          visibility: hidden;
        }
         .collapse-btn {
           display: none;
         }
      }
  }
  .user-profile-list-item {
      transition: padding 0.2s ease-in-out, min-height 0.2s ease-in-out;
      overflow: hidden;
  
      .v-list-item__prepend .v-avatar {
          margin-inline-end: 16px;
          transition: margin 0.2s ease-in-out;
      }
  
      .v-list-item-title {
          font-weight: 600;
          font-size: 0.9rem;
          line-height: 1.3;
          color: rgb(var(--v-theme-on-surface));
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          transition: opacity 0.1s linear;
      }
       .v-list-item-subtitle {
          font-size: 0.75rem;
          color: rgba(var(--v-theme-on-surface-rgb), 0.65);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          transition: opacity 0.1s linear;
      }
      .collapse-btn {
          color: rgba(var(--v-theme-on-surface-rgb), 0.5);
          transition: color 0.2s;
          &:hover {
              color: rgb(var(--v-theme-on-surface));
          }
      }
  }
  .v-navigation-drawer--rail {
      .user-profile-list-item {
          .v-list-item__prepend .v-avatar {
              margin-inline-end: 0px;
          }
      }
  }
  .drawer-list-item {
      transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out, padding 0.2s ease-in-out;
     .v-list-item-title {
        font-size: 0.9rem !important;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
     }
     .v-list-item__prepend > .v-icon {
        margin-inline-end: 18px !important;
        opacity: 0.75;
        transition: opacity 0.15s ease-in-out, margin 0.2s ease-in-out;
     }
    &:hover {
      background-color: rgba(var(--v-theme-primary-rgb), 0.07) !important;
      color: rgb(var(--v-theme-primary)) !important;
      .v-list-item__prepend > .v-icon {
         opacity: 1;
      }
    }
    &.drawer-list-item--active {
      background-color: rgba(var(--v-theme-primary-rgb), 0.12) !important;
      color: rgb(var(--v-theme-primary)) !important;
      .v-list-item-title {
         font-weight: 600;
      }
      .v-list-item__prepend > .v-icon {
         opacity: 1;
         color: rgb(var(--v-theme-primary)) !important;
      }
    }
  }
  .v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) {
      .drawer-list-item .v-list-item-title {
          opacity: 0;
          visibility: hidden;
      }
      .drawer-list-item .v-list-item__prepend > .v-icon {
        margin-inline-end: 0px !important;
      }
  }
  .drawer-append-logout {
      margin-bottom: 8px;
      transition: padding 0.2s ease-in-out;
     .logout-btn span {
         font-weight: 500;
     }
  }
  .v-navigation-drawer--rail:not(.v-navigation-drawer--is-hovering) {
      .drawer-append-logout {
          padding-left: 0 !important;
          padding-right: 0 !important;
          text-align: center;
      }
      .drawer-append-logout .logout-btn span {
          display: none;
      }
  }
  .app-bar-border {
    border-bottom: 1px solid rgba(var(--v-theme-on-surface-rgb), 0.08) !important;
    transition: padding-left 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  }
  .app-title {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: rgb(var(--v-theme-on-surface)) !important;
    letter-spacing: -0.01em;
    transition: margin-left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .expand-from-rail-btn {
      color: rgba(var(--v-theme-on-surface-rgb), 0.7);
      margin-left: -8px;
      &:hover {
         color: rgb(var(--v-theme-on-surface));
      }
  }
  .auth-btn {
    font-weight: 500;
    letter-spacing: 0.01em;
    text-transform: none;
    border-radius: 6px;
    &.v-btn--variant-text {
      color: rgba(var(--v-theme-on-surface-rgb), 0.85);
       &:hover {
         color: rgb(var(--v-theme-on-surface));
      }
    }
     &.v-btn--variant-flat {
       color: rgb(var(--v-theme-on-primary)) !important;
     }
  }
  .main-content-area {
    transition: padding-left 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    overflow-x: hidden;
  }
  </style>