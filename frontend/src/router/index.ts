import { createRouter, createWebHistory } from "vue-router";
import AppLayout from '@/layouts/AppLayout.vue'; // Nuevo Layout
import ProfileView from "../views/ProfileView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import { useAuthStore } from "@/stores/auth";

const routes = [
  { path: "/login", name: "Login", component: LoginView },
  { path: "/register", name: "Register", component: RegisterView },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: ProfileView,
        meta: { title: 'Dashboard' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: ProfileView,
        meta: { title: 'Projects' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: ProfileView,
        meta: { title: 'Profile' }
      },
    ]
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = !!authStore.token;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else if (!to.meta.requiresAuth && isAuthenticated) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;