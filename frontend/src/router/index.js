import { createRouter, createWebHistory } from 'vue-router';

const DefaultLayout = () => import('@/layouts/DefaultLayout.vue');

const LoginPage = () => import('../views/LoginPage.vue');
const RegisterPage = () => import('../views/RegisterPage.vue');
const TaskListView = () => import('../views/tasks/TaskListView.vue');
const UserListView = () => import('../views/users/UserListView.vue');
const NotificationsPage = () => import('../views/notifications/NotificationsPage.vue');
const TaskListOptionsView = () => import('../views/tasksoptions/TaskListView.vue');


const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true, hideSidebar: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresGuest: true, hideSidebar: true }
  },
  {
    path: '/',
    component: DefaultLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/tasks' },
      {
        path: 'tasks',
        name: 'TaskList',
        component: TaskListView,
      },
      {
        path: 'tasks-options',
        name: 'TaskListOptions',
        component: TaskListOptionsView,
      },
      {
        path: 'users',
        name: 'UserList',
        component: UserListView,
        meta: {
          requiresAdminOrManager: true,
        },
      },
      {
        path: 'notifications',
        name: 'NotificationsPage',
        component: NotificationsPage,
      },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: () => {
        const token = localStorage.getItem('authToken');
        return token ? { name: 'TaskList' } : { name: 'Login' };
    }
  }

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

  if (needsAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (needsGuest && isAuthenticated) {
    next({ name: 'TaskList' });
  } else {
    if (needsAuth && isAuthenticated) {
        const needsAdminOrManager = to.matched.some(record => record.meta.requiresAdminOrManager);
        if (needsAdminOrManager && !(userRole === 'ADMIN' || userRole === 'MANAGER')) {
            next({ name: 'TaskList' });
            return;
        }
    }
    next();
  }
});

export default router;