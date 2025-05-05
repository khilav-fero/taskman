import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const LoginPage = () => import('../views/LoginPage.vue');
const RegisterPage = () => import('../views/RegisterPage.vue');
const TaskListView = () => import('../views/TaskListView.vue');
const UserListView = () => import('../views/UserListView.vue'); // Ensure this exists

const routes = [
  { path: '/', redirect: '/tasks' },
  { path: '/login', name: 'Login', component: LoginPage, meta: { requiresGuest: true } },
  { path: '/register', name: 'Register', component: RegisterPage, meta: { requiresGuest: true } },
  { path: '/tasks', name: 'TaskList', component: TaskListView, meta: { requiresAuth: true } },
  {
    path: '/users',
    name: 'UserList',
    component: UserListView,
    meta: {
        requiresAuth: true,
        requiresAdminOrManager: true // RBAC
    }
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  const isAuthenticated = authStore.getIsAuthenticated;
  const role = authStore.userRole;

  const needsAuth = to.matched.some(record => record.meta.requiresAuth);
  const needsGuest = to.matched.some(record => record.meta.requiresGuest);
  const needsAdminOrManager = to.matched.some(record => record.meta.requiresAdminOrManager);

  if (needsAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (needsGuest && isAuthenticated) {
    next({ name: 'TaskList' });
  } else if (needsAdminOrManager && !(role === 'ADMIN' || role === 'MANAGER')) {
    console.warn(`Guard: Access denied to ${to.path}. Requires ADMIN or MANAGER role.`);
    next({ name: 'TaskList' }); // Redirect non-admins/managers away
  }
  else {
    next(); // Allow
  }
});

export default router;