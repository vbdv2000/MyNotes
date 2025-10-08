import { createRouter, createWebHistory } from "vue-router";
import AppLayout from '@/layouts/AppLayout.vue';
import ProfileView from "../views/ProfileView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import ProjectsView from "../views/ProjectsView.vue";
import KanbanView from "../views/KanbanView.vue";
import NotificationsView from "../views/NotificationsView.vue";
import TagsView from "../views/TagsView.vue";

import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/login", name: "Login", component: LoginView },
  { path: "/register", name: "Register", component: RegisterView },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Home', component: ProfileView, meta: { title: 'Dashboard' } },

      // Vista de todos los proyectos
      { path: 'projects', name: 'Projects', component: ProjectsView, meta: { title: 'Todos los Proyectos' } },

      // Vista del tablero Kanban por ID de proyecto (Punto Clave)
      {
        path: 'projects/:id/kanban',
        name: 'ProjectKanban',
        component: KanbanView,
        meta: { title: 'Tablero Kanban' }
      },

      // Otras utilidades
      { path: 'notifications', name: 'Notifications', component: NotificationsView, meta: { title: 'Notificaciones' } },
      { path: 'tags', name: 'Tags', component: TagsView, meta: { title: 'Gestión de Tags' } },
      { path: 'profile', name: 'Profile', component: ProfileView, meta: { title: 'Perfil' } },
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