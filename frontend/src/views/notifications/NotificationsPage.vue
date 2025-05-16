<template>
    <v-container fluid class="pa-md-6 pa-4">
      <div class="d-flex justify-space-between align-center mb-6">
        <h1 class="text-h4 font-weight-medium">Notifications</h1>
        <v-btn
          v-if="notifications.some(n => !n.read) && !isLoading"
          color="primary"
          variant="tonal"
          @click="handleMarkAllRead"
          :loading="isMarkingAllRead"
        >
          Mark All as Read
        </v-btn>
      </div>
  
      <v-card :loading="isLoading" variant="flat" class="card-container" rounded="lg">
        <v-card-text class="pa-0">
          <v-tabs v-model="activeFilter" color="primary" grow @update:model-value="onFilterChange">
            <v-tab value="all">All</v-tab>
            <v-tab value="unread">Unread</v-tab>
            <v-tab value="read">Read</v-tab>
          </v-tabs>
          <v-divider></v-divider>
  
          <v-progress-linear v-if="isLoading" indeterminate color="primary"></v-progress-linear>
  
          <v-alert v-if="error" type="error" variant="tonal" density="compact" class="ma-4">
            {{ error }}
          </v-alert>
  
          <v-list v-if="!isLoading && notifications.length > 0" lines="two" density="comfortable" class="py-0">
            <template v-for="(notification, index) in notifications" :key="notification.id">
              <v-list-item
                @click="handleNotificationClick(notification)"
                :class="{ 'font-weight-medium unread-notification': !notification.read, 'read-notification': notification.read }"
                class="notification-page-item"
              >
                <template v-slot:prepend>
                  <v-avatar :color="!notification.read ? 'primary' : 'grey-lighten-2'" size="40" class="mr-4">
                    <v-icon :color="!notification.read ? 'white' : 'grey-darken-1'">{{ getNotificationIcon(notification) }}</v-icon>
                  </v-avatar>
                </template>
  
                <v-list-item-title class="text-body-1" style="white-space: normal;">{{ notification.message }}</v-list-item-title>
                <v-list-item-subtitle class="text-caption">{{ formatRelativeTime(notification.timestamp) }}</v-list-item-subtitle>
  
                <template v-slot:append v-if="!notification.read">
                   <v-btn icon variant="text" size="small" @click.stop="markSingleAsRead(notification)">
                      <v-icon color="primary" title="Mark as read">mdi-check-circle-outline</v-icon>
                       <v-tooltip activator="parent" location="top">Mark as read</v-tooltip>
                   </v-btn>
                </template>
              </v-list-item>
              <v-divider v-if="index < notifications.length - 1"></v-divider>
            </template>
          </v-list>
  
          <div v-else-if="!isLoading && notifications.length === 0 && !error" class="text-center pa-10 text-medium-emphasis">
            <v-icon size="64" class="mb-3">mdi-email-open-outline</v-icon>
            <p class="text-h6">No notifications to display.</p>
            <p v-if="activeFilter === 'unread'">You're all caught up!</p>
          </div>
  
          <div v-if="totalPages > 1 && !isLoading" class="text-center pa-4">
            <v-pagination
              v-model="currentPage"
              :length="totalPages"
              :total-visible="7"
              @update:model-value="handlePageChange"
              density="compact"
            ></v-pagination>
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead
  } from '@/services/notificationService';
  
  const router = useRouter();
  
  const notifications = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const isMarkingAllRead = ref(false);
  
  const currentPage = ref(1);
  const itemsPerPage = ref(15);
  const totalNotifications = ref(0);
  
  const activeFilter = ref('all');
  
  const totalPages = computed(() => {
    return Math.ceil(totalNotifications.value / itemsPerPage.value);
  });
  
  const loadNotifications = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const params = {
        page: currentPage.value,
        page_size: itemsPerPage.value,
      };
      if (activeFilter.value === 'unread') {
        params.read = false;
      } else if (activeFilter.value === 'read') {
        params.read = true;
      }
  
      const data = await fetchNotifications(params);
      notifications.value = data.results || [];
      totalNotifications.value = data.count || 0;
    } catch (err) {
      console.error("Failed to load notifications:", err);
      error.value = "Could not load notifications. Please try again.";
      notifications.value = [];
      totalNotifications.value = 0;
    } finally {
      isLoading.value = false;
    }
  };
  
  const handleNotificationClick = async (notification) => {
    if (notification.related_task) {
       router.push({ name: 'TaskList' });
    }
    if (!notification.read) {
      await markSingleAsRead(notification);
    }
  };
  
  const markSingleAsRead = async (notification) => {
      try {
        const updatedNotification = await markNotificationAsRead(notification.id);
        const index = notifications.value.findIndex(n => n.id === notification.id);
        if (index !== -1) {
          notifications.value[index] = updatedNotification;
        }
        if (activeFilter.value === 'unread') {
          notifications.value = notifications.value.filter(n => n.id !== notification.id);
          if (totalNotifications.value > 0) totalNotifications.value--;
        }
      } catch (error) {
        console.error("Failed to mark notification as read", error);
      }
  };
  
  const handleMarkAllRead = async () => {
    isMarkingAllRead.value = true;
    try {
      await markAllNotificationsAsRead();
      notifications.value.forEach(n => n.read = true);
      if (activeFilter.value === 'unread') {
          notifications.value = [];
          totalNotifications.value = 0;
      }
    } catch (err) {
      console.error("Failed to mark all as read", err);
      error.value = "Could not mark all as read.";
    } finally {
      isMarkingAllRead.value = false;
    }
  };
  
  const onFilterChange = () => {
    currentPage.value = 1;
    loadNotifications();
  };
  
  const handlePageChange = (page) => {
    currentPage.value = page;
    loadNotifications();
  };
  
  const formatRelativeTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffSeconds = Math.round((now - date) / 1000);
    if (diffSeconds < 60) return `${diffSeconds}s ago`;
    const diffMinutes = Math.round(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.round(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.round(diffHours / 24);
    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleString(undefined, { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit' });
  };
  
  const getNotificationIcon = (notification) => {
    if (notification.message?.toLowerCase().includes('assigned')) return 'mdi-account-plus-outline';
    if (notification.message?.toLowerCase().includes('commented')) return 'mdi-comment-text-outline';
    if (notification.message?.toLowerCase().includes('updated')) return 'mdi-pencil-circle-outline';
    if (notification.message?.toLowerCase().includes('deadline')) return 'mdi-calendar-alert';
    return 'mdi-information-outline';
  };
  
  onMounted(() => {
    loadNotifications();
  });
  </script>
  
  <style scoped>
  .card-container {
    border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  }
  .unread-notification {
    background-color: rgba(var(--v-theme-primary-rgb), 0.05);
  }
  .read-notification {
    opacity: 0.75;
  }
  .notification-page-item:hover {
    background-color: rgba(var(--v-theme-on-surface-rgb), 0.04);
  }
  </style>