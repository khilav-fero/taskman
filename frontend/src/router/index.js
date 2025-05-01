// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const LoginPage = () => import('../views/LoginPage.vue');
const RegisterPage = () => import('../views/RegisterPage.vue');
// --- CHANGE THIS ---
const TaskListView = () => import('../views/TaskListView.vue'); // Import the actual view

const routes = [
  {
    path: '/',
    redirect: '/tasks' // Can now safely redirect to tasks
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/tasks',
    name: 'TaskList',
    // --- USE THE REAL COMPONENT ---
    component: TaskListView,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// --- Navigation Guard (Unchanged from previous version) ---
router.beforeEach(async (to, from, next) => {
   // ... (same guard logic as before) ...
    const authStore = useAuthStore();
    const isAuthenticated = authStore.getIsAuthenticated;
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const requiresGuest = to.matched.some(record => record.meta.requiresGuest);

    if (requiresAuth && !isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } });
    } else if (requiresGuest && isAuthenticated) {
        next({ name: 'TaskList' });
    } else {
        next();
    }
});

export default router;