import { createRouter, createWebHistory } from 'vue-router';

const LoginPage = () => import('../views/LoginPage.vue');
const RegisterPage = () => import('../views/RegisterPage.vue');
const TaskListView = () => import('../views/TaskListView.vue');
const UserListView = () => import('../views/UserListView.vue');

const routes = [
  { path: '/', redirect: '/tasks' },
  { path: '/login', name: 'Login', component: LoginPage, meta: { requiresGuest: true, hideSidebar: true } },
  { path: '/register', name: 'Register', component: RegisterPage, meta: { requiresGuest: true, hideSidebar: true } },
  { path: '/tasks', name: 'TaskList', component: TaskListView, meta: { requiresAuth: true } },
  {
    path: '/users',
    name: 'UserList',
    component: UserListView,
    meta: {
      requiresAuth: true,
      requiresAdminOrManager: true,
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('authToken');
  let user = null;
  const storedUser = localStorage.getItem('authUser');

  if (storedUser) {
    try {
      user = JSON.parse(storedUser);
    } catch (e) {
      localStorage.removeItem('authUser');
    }
  }

  const isAuthenticated = !!token;
  const userRole = user?.profile?.role || null;

  const needsAuth = to.matched.some(record => record.meta.requiresAuth);
  const needsGuest = to.matched.some(record => record.meta.requiresGuest);
  const needsAdminOrManager = to.matched.some(record => record.meta.requiresAdminOrManager);

  if (needsAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (needsGuest && isAuthenticated) {
    next({ name: 'TaskList' });
  } else if (needsAdminOrManager) {
    if (!isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } });
    } else if (!(userRole === 'ADMIN' || userRole === 'MANAGER')) {
        next({ name: 'TaskList' });
    } else {
        next();
    }
  }
  else {
    next();
  }
});

export default router;