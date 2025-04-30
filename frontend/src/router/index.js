import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth'; 

const LoginPage = () => import('../views/LoginPage.vue');
const RegisterPage = () => import('../views/RegisterPage.vue');
const TaskListPlaceholder = { template: '<div style="padding:20px;"><h1>Tasks</h1><p>Task list will appear here.</p></div>' };

const routes = [
  {
    path: '/',
    redirect: '/tasks' 
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
    name: 'TaskList', // Name for navigation
    component: TaskListPlaceholder, // Use placeholder
    meta: { requiresAuth: true } // Requires login
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(); 
  const isAuthenticated = authStore.getIsAuthenticated; 

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);

  if (requiresAuth && !isAuthenticated) {
    console.log(`Guard: Navigating to '${to.name?.toString()}' requires auth. Redirecting to Login.`);
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (requiresGuest && isAuthenticated) {
    console.log(`Guard: Navigating to guest route '${to.name?.toString()}' while logged in. Redirecting to TaskList.`);
    next({ name: 'TaskList' });
  } else {
    next();
  }
});

export default router;