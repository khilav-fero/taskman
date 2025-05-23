<template>
    <v-container fluid class="pa-md-6 pa-4 notification-page-container">
      <div class="d-flex justify-space-between align-center mb-6">
        <h1 class="text-h4 font-weight-medium">Notifications</h1>
        <v-btn
          v-if="notifications.some(n => !n.read) && !isLoadingInitial"
          color="primary"
          variant="tonal"
          @click="handleMarkAllRead"
          :loading="isMarkingAllRead"
        >
          Mark All as Read
        </v-btn>
      </div>
  
      <v-card :loading="isLoadingInitial && notifications.length === 0" variant="flat" class="card-container" rounded="lg">
        <v-card-text class="pa-0">
          <v-tabs v-model="activeFilter" color="primary" grow @update:model-value="onFilterChange">
            <v-tab value="all">All</v-tab>
            <v-tab value="unread">Unread</v-tab>
            <v-tab value="read">Read</v-tab>
          </v-tabs>
          <v-divider></v-divider>
  
          <v-progress-linear v-if="isLoadingInitial && notifications.length === 0" indeterminate color="primary"></v-progress-linear>
  
          <v-alert v-if="error" type="error" variant="tonal" density="compact" class="ma-4">
            {{ error }}
          </v-alert>
  
          <div class="notification-list-wrapper" ref="scrollContainerRef">
            <v-list v-if="notifications.length > 0" lines="two" density="comfortable" class="py-0">
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
  
            <div v-if="isLoadingMore" class="text-center pa-4">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
  
            <div
              v-if="!isLoadingInitial && !isLoadingMore && notifications.length === 0 && !error"
              class="text-center pa-10 text-medium-emphasis no-notifications-message"
            >
              <v-icon size="64" class="mb-3">mdi-email-open-outline</v-icon>
              <p class="text-h6">No notifications to display.</p>
              <p v-if="activeFilter === 'unread'">You're all caught up!</p>
            </div>
  
            <div
              v-if="noMoreNotifications && notifications.length > 0 && !isLoadingInitial && !isLoadingMore"
              class="text-center pa-4 text-medium-emphasis"
            >
              <v-icon size="24" class="mr-1">mdi-check-all</v-icon>
              All notifications loaded.
            </div>
  
            <div ref="scrollSentinelRef"></div>
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead
  } from '@/services/notificationService';
  
  const router = useRouter();
  
  const notifications = ref([]);
  const isLoadingInitial = ref(false);
  const isLoadingMore = ref(false);
  const error = ref(null);
  const isMarkingAllRead = ref(false);
  
  const itemsPerPage = ref(15);
  const nextPageUrl = ref(null); // Still here for API version, unused by mock
  const noMoreNotifications = ref(false);
  const activeFilter = ref('all');
  
  const scrollSentinelRef = ref(null);
  let observer = null;
  
  // --- START MOCK DATA GENERATION ---
  let allMockNotifications = [];
  let mockCurrentPageIndex = 0;
  const USE_MOCK_DATA = false; // SET TO true TO USE MOCK DATA, false FOR API
  
  function generateMockNotifications(count = 50) {
    const mockNotificationsList = [];
    const messages = [
      "Your task 'Deploy to Production' is due tomorrow.",
      "Alice commented on 'User Authentication Flow': 'Looks good to me!'",
      "Bob assigned you to 'Fix Login Bug'.",
      "The status of 'API Integration' was changed to In Progress.",
      "You were mentioned in 'Project Alpha Kickoff' by Charlie: '@testuser can you confirm your availability?'",
      "New task 'Client Demo Prep' was created by David.",
      "Deadline for 'Documentation Review' is approaching.",
      "Eve updated the description for 'UI Mockups V2'.",
      "Frank added you as a collaborator to 'Security Audit'.",
      "Grace marked 'Performance Testing' as Done."
    ];
    const usernames = ["alice", "bob", "charlie", "david", "eve", "frank", "grace", "heidi", "ivan"];
  
    for (let i = 0; i < count; i++) {
      const randomMessageIndex = Math.floor(Math.random() * messages.length);
      const randomUsernameIndex = Math.floor(Math.random() * usernames.length);
      const randomTimestampMillis = new Date().getTime() - Math.floor(Math.random() * 1000 * 60 * 60 * 24 * 30);
  
      let readStatus = Math.random() < 0.7;
      if (activeFilter.value === 'unread') readStatus = false;
      else if (activeFilter.value === 'read') readStatus = true;
  
  
      mockNotificationsList.push({
        id: `mock-${Date.now()}-${i}-${Math.random()}`,
        message: messages[randomMessageIndex],
        timestamp: new Date(randomTimestampMillis).toISOString(),
        read: readStatus,
        related_task: Math.random() < 0.5 ? Math.floor(Math.random() * 100) + 1 : null,
        actor: { username: usernames[randomUsernameIndex] }
      });
    }
    return mockNotificationsList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }
  
  const loadMockInitialNotifications = () => {
    isLoadingInitial.value = true;
    error.value = null;
    notifications.value = [];
    noMoreNotifications.value = false;
    mockCurrentPageIndex = 0;
  
    if (allMockNotifications.length === 0 || activeFilter.value !== 'all') { // Regenerate if filter changes from all
        allMockNotifications = generateMockNotifications(200);
    }
  
    let filteredMocks = allMockNotifications;
    if (activeFilter.value === 'unread') {
      filteredMocks = allMockNotifications.filter(n => !n.read);
    } else if (activeFilter.value === 'read') {
      filteredMocks = allMockNotifications.filter(n => n.read);
    }
    
    // Store filtered mocks to paginate from them correctly
    // This simulates what the backend filter would do
    const currentFilteredSet = [...filteredMocks];
  
  
    const startIndex = mockCurrentPageIndex * itemsPerPage.value;
    const endIndex = startIndex + itemsPerPage.value;
    const pageResults = currentFilteredSet.slice(startIndex, endIndex);
  
    notifications.value = pageResults;
    mockCurrentPageIndex++;
  
    if (endIndex >= currentFilteredSet.length) {
      noMoreNotifications.value = true;
    }
    isLoadingInitial.value = false;
  };
  
  const loadMockMoreNotifications = async () => {
    if (isLoadingMore.value || noMoreNotifications.value) return;
  
    isLoadingMore.value = true;
  
    let filteredMocks = allMockNotifications;
     if (activeFilter.value === 'unread') {
      filteredMocks = allMockNotifications.filter(n => !n.read);
    } else if (activeFilter.value === 'read') {
      filteredMocks = allMockNotifications.filter(n => n.read);
    }
    const currentFilteredSet = [...filteredMocks];
  
    const startIndex = mockCurrentPageIndex * itemsPerPage.value;
    const endIndex = startIndex + itemsPerPage.value;
    const pageResults = currentFilteredSet.slice(startIndex, endIndex);
  
    await new Promise(resolve => setTimeout(resolve, 300));
  
    notifications.value.push(...pageResults);
    mockCurrentPageIndex++;
  
    if (endIndex >= currentFilteredSet.length) {
      noMoreNotifications.value = true;
    }
    isLoadingMore.value = false;
  };
  // --- END MOCK DATA GENERATION ---
  
  const loadInitialNotifications = async () => {
    if (USE_MOCK_DATA) {
      loadMockInitialNotifications();
      setTimeout(() => setupIntersectionObserver(), 0); // Ensure observer is setup after mock data potentially fills screen
      return;
    }
  
    isLoadingInitial.value = true;
    error.value = null;
    notifications.value = [];
    nextPageUrl.value = null;
    noMoreNotifications.value = false;
  
    try {
      const params = {
        page: 1,
        page_size: itemsPerPage.value,
      };
      if (activeFilter.value === 'unread') {
        params.read = false;
      } else if (activeFilter.value === 'read') {
        params.read = true;
      }
  
      const data = await fetchNotifications(params);
      notifications.value = data.results || [];
      nextPageUrl.value = data.next || null;
      if (!nextPageUrl.value && (data.results || []).length < itemsPerPage.value) {
        noMoreNotifications.value = true;
      } else if (!nextPageUrl.value && (data.count !== undefined && data.results !==undefined && data.count === data.results.length)) {
        noMoreNotifications.value = true;
      }
    } catch (err) {
      console.error("Failed to load initial notifications:", err);
      error.value = "Could not load notifications. Please try again.";
      notifications.value = [];
    } finally {
      isLoadingInitial.value = false;
      setupIntersectionObserver();
    }
  };
  
  const loadMoreNotifications = async () => {
    if (USE_MOCK_DATA) {
      loadMockMoreNotifications();
      return;
    }
  
    if (isLoadingMore.value || !nextPageUrl.value || noMoreNotifications.value) {
      return;
    }
  
    isLoadingMore.value = true;
    error.value = null;
  
    try {
      const url = new URL(nextPageUrl.value);
      const params = {};
      url.searchParams.forEach((value, key) => {
        params[key] = value;
      });
      
      const data = await fetchNotifications(params);
      notifications.value.push(...(data.results || []));
      nextPageUrl.value = data.next || null;
      if (!nextPageUrl.value) {
        noMoreNotifications.value = true;
      }
    } catch (err) {
      console.error("Failed to load more notifications:", err);
      error.value = "Could not load more notifications. Please try again.";
    } finally {
      isLoadingMore.value = false;
    }
  };
  
  const setupIntersectionObserver = () => {
    if (observer) {
      observer.disconnect();
    }
    if (!scrollSentinelRef.value) return;
  
    const options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.5
    };
  
    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !isLoadingInitial.value && !isLoadingMore.value && !noMoreNotifications.value) {
        if (USE_MOCK_DATA || nextPageUrl.value) { // Check nextPageUrl only if not using mocks
           loadMoreNotifications();
        }
      }
    }, options);
  
    if (scrollSentinelRef.value) {
      observer.observe(scrollSentinelRef.value);
    }
  };
  
  
  const handleNotificationClick = async (notification) => {
    if (notification.related_task) {
       router.push({ name: 'TaskList', query: { openTaskDetail: notification.related_task } });
    }
    if (!notification.read) {
      await markSingleAsRead(notification);
    }
  };
  
  const markSingleAsRead = async (notification) => {
      if (notification.read && !USE_MOCK_DATA) return;
      
      if (USE_MOCK_DATA) {
          const index = notifications.value.findIndex(n => n.id === notification.id);
          if (index !== -1) {
              notifications.value[index].read = true;
              if (activeFilter.value === 'unread') {
                  notifications.value = notifications.value.filter(n => !n.read);
                   if (notifications.value.length === 0) noMoreNotifications.value = true;
              }
          }
          return;
      }
  
      try {
        const updatedNotification = await markNotificationAsRead(notification.id);
        const index = notifications.value.findIndex(n => n.id === notification.id);
        if (index !== -1) {
          notifications.value[index] = { ...notifications.value[index], ...updatedNotification, read: true };
          if (activeFilter.value === 'unread') {
             notifications.value = notifications.value.filter(n => !n.read);
             if (notifications.value.length === 0) noMoreNotifications.value = true; // If unread list becomes empty
          }
        }
      } catch (error) {
        console.error("Failed to mark notification as read", error);
      }
  };
  
  const handleMarkAllRead = async () => {
    isMarkingAllRead.value = true;
  
    if (USE_MOCK_DATA) {
        notifications.value.forEach(n => n.read = true);
        if (activeFilter.value === 'unread') {
            notifications.value = [];
            noMoreNotifications.value = true;
        }
        isMarkingAllRead.value = false;
        return;
    }
  
    try {
      await markAllNotificationsAsRead();
      notifications.value.forEach(n => {
          if (!n.read) n.read = true;
      });
       if (activeFilter.value === 'unread') {
          notifications.value = [];
          noMoreNotifications.value = true;
      }
    } catch (err) {
      console.error("Failed to mark all as read", err);
      error.value = "Could not mark all as read.";
    } finally {
      isMarkingAllRead.value = false;
    }
  };
  
  const onFilterChange = () => {
    loadInitialNotifications();
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
    const messageLower = notification.message?.toLowerCase() || '';
    if (messageLower.includes('assigned to task') || messageLower.includes('added you as a collaborator')) return 'mdi-account-plus-outline';
    if (messageLower.includes('commented on task') || messageLower.includes('mentioned you in a comment')) return 'mdi-comment-text-outline';
    if (messageLower.includes('updated task') || messageLower.includes('task status changed')) return 'mdi-pencil-circle-outline';
    if (messageLower.includes('deadline approaching') || messageLower.includes('deadline updated')) return 'mdi-calendar-alert';
    if (messageLower.includes('task created')) return 'mdi-file-document-plus-outline';
    return 'mdi-information-outline';
  };
  
  onMounted(() => {
    loadInitialNotifications();
  });
  
  onBeforeUnmount(() => {
    if (observer) {
      observer.disconnect();
    }
  });
  
  watch(activeFilter, () => {
      // The observer is re-setup in loadInitialNotifications's finally block
  });
  
  </script>
  
  <style scoped>
  .notification-page-container {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .card-container {
    border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .v-card-text {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .notification-list-wrapper {
    flex-grow: 1;
    overflow-y: auto;
  }
  .unread-notification {
    background-color: rgba(var(--v-theme-primary-rgb), 0.05);
  }
  .read-notification {
    opacity: 0.75;
  }
  .notification-page-item {
    cursor: pointer;
    transition: background-color 0.15s ease-in-out;
  }
  .notification-page-item:hover {
    background-color: rgba(var(--v-theme-on-surface-rgb), 0.04);
  }
  .no-notifications-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 200px;
  }
  </style>