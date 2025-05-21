<template>
    <v-menu
      v-model="isMenuOpen"
      :close-on-content-click="false"
      location="bottom end"
      offset="12"
      max-width="400px"
      min-width="350px"
    >
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props" @click="onBellClick" class="mx-1">
          <v-badge :content="unreadCount > 0 ? unreadCount : undefined" :model-value="unreadCount > 0" color="error" dot overlap>
            <v-icon>{{ unreadCount > 0 ? 'mdi-bell' : 'mdi-bell-outline' }}</v-icon>
          </v-badge>
          <v-tooltip activator="parent" location="bottom">Notifications</v-tooltip>
        </v-btn>
      </template>
  
      <v-card :loading="isLoadingList">
        <v-card-title class="d-flex justify-space-between align-center py-2 px-3 text-subtitle-1">
          Notifications
          <v-btn
            v-if="notifications.some(n => !n.read)"
            size="small"
            variant="text"
            color="primary"
            @click.stop="handleMarkAllRead"
            :loading="isMarkingAllRead"
          >
            Mark all as read
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
  
        <v-alert v-if="listError" type="error" density="compact" variant="tonal" class="ma-2">
          {{ listError }}
        </v-alert>
  
        <v-list v-if="!isLoadingList && notifications.length > 0" lines="two" density="compact" class="py-0 notification-list">
          <template v-for="notification in notifications" :key="notification.id">
            <v-list-item
              @click="handleNotificationClick(notification)"
              :class="{ 'font-weight-bold unread-notification': !notification.read, 'read-notification': notification.read }"
              class="notification-item"
            >
              <template v-slot:prepend>
                <v-icon size="small" class="mr-3" :color="!notification.read ? 'primary' : 'grey'">
                  {{ getNotificationIcon(notification) }}
                </v-icon>
              </template>
              <v-list-item-title class="text-body-2" style="white-space: normal;">{{ notification.message }}</v-list-item-title>
              <v-list-item-subtitle class="text-caption">{{ formatRelativeTime(notification.timestamp) }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider></v-divider>
          </template>
        </v-list>
  
        <div v-else-if="!isLoadingList && notifications.length === 0 && !listError" class="text-center pa-8 text-medium-emphasis">
          <v-icon size="48" class="mb-2">mdi-bell-sleep-outline</v-icon>
          <p>No new notifications.</p>
        </div>
        <v-divider></v-divider>
        <v-card-actions class="justify-center pa-2">
          <v-btn variant="text" color="primary" block @click="navigateToNotificationsPage">
            View All Notifications
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    fetchUnreadNotificationCount,
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead
  } from '@/services/notificationService';
  
  const router = useRouter();
  
  const unreadCount = ref(0);
  const notifications = ref([]);
  const isLoadingCount = ref(false);
  const isLoadingList = ref(false);
  const isMenuOpen = ref(false);
  const listError = ref(null);
  const isMarkingAllRead = ref(false);
  
  const loadUnreadCount = async () => {
    isLoadingCount.value = true;
    try {
      const data = await fetchUnreadNotificationCount();
      unreadCount.value = data.unread_count || 0;
    } catch (error) {
      console.error("Failed to load unread notification count", error);
    } finally {
      isLoadingCount.value = false;
    }
  };
  
  const loadRecentNotifications = async () => {
    if (!isMenuOpen.value) return;
    isLoadingList.value = true;
    listError.value = null;
    try {
      const data = await fetchNotifications({ page_size: 7 });
      notifications.value = data.results || [];
    } catch (error) {
      console.error("Failed to load recent notifications", error);
      listError.value = "Could not load notifications.";
    } finally {
      isLoadingList.value = false;
    }
  };
  
  const handleNotificationClick = async (notification) => {
    isMenuOpen.value = false;
    if (notification.related_task) {
      router.push({ name: 'TaskList' });
    }
    if (!notification.read) {
      try {
        const updatedNotification = await markNotificationAsRead(notification.id);
        const index = notifications.value.findIndex(n => n.id === notification.id);
        if (index !== -1) {
          notifications.value[index] = updatedNotification;
        }
        if (unreadCount.value > 0) {
           const stillUnreadInList = notifications.value.filter(n => !n.read).length;
           const unreadElsewhere = unreadCount.value - (notifications.value.length - stillUnreadInList);
           unreadCount.value = Math.max(0, unreadElsewhere + stillUnreadInList -1);
           if (notifications.value.every(n => n.read)) { // if all in dropdown are read
              loadUnreadCount(); // refresh count accurately
           }
        }
      } catch (error) {
        console.error("Failed to mark notification as read", error);
      }
    }
  };
  
  const handleMarkAllRead = async () => {
    isMarkingAllRead.value = true;
    try {
      await markAllNotificationsAsRead();
      notifications.value.forEach(n => n.read = true);
      unreadCount.value = 0;
    } catch (error) {
      console.error("Failed to mark all as read", error);
      listError.value = "Could not mark all as read.";
    } finally {
      isMarkingAllRead.value = false;
      isMenuOpen.value = false;
    }
  };
  
  const navigateToNotificationsPage = () => {
    isMenuOpen.value = false;
    router.push({ name: 'NotificationsPage' });
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
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };
  
  const getNotificationIcon = (notification) => {
    if (notification.message?.toLowerCase().includes('assigned')) return 'mdi-account-plus-outline';
    if (notification.message?.toLowerCase().includes('commented')) return 'mdi-comment-text-outline';
    if (notification.message?.toLowerCase().includes('updated')) return 'mdi-pencil-circle-outline';
    if (notification.message?.toLowerCase().includes('deadline')) return 'mdi-calendar-alert';
    return 'mdi-information-outline';
  };
  
  const onBellClick = () => {
    if (!isMenuOpen.value) {
      listError.value = null;
      loadRecentNotifications();
    }
  };    
  
  onMounted(() => {
    loadUnreadCount();
  });
  
  watch(isMenuOpen, (isOpen) => {
    if (isOpen) {
      listError.value = null;
      loadRecentNotifications();
    }
  });
  </script>
  
  <style scoped>
  .notification-list {
    max-height: 400px;
    overflow-y: auto;
  }
  .unread-notification {
    background-color: rgba(var(--v-theme-primary-rgb), 0.05);
  }
  .read-notification {
    opacity: 0.8;
  }
  .notification-item:hover {
    background-color: rgba(var(--v-theme-on-surface-rgb), 0.04);
  }
  </style>