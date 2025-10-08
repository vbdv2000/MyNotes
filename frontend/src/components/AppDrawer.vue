<template>
  <v-navigation-drawer
    expand-on-hover
    rail
    permanent
    color="surface" 
    app
  >
    <v-list>
      <v-list-item 
        prepend-icon="mdi-note-multiple-outline"
        title="MyNotes App"
        class="text-primary font-weight-bold"
        to="/"
      />
    </v-list>
    
    <v-divider></v-divider>

    <v-list density="compact" nav>
      
      <v-list-item 
        prepend-icon="mdi-view-dashboard-outline" 
        title="Dashboard" 
        value="home" 
        :to="{ name: 'Home' }"
        active-class="text-primary"
      />
      
      <v-list-item 
        prepend-icon="mdi-format-list-bulleted-square" 
        title="Proyectos" 
        value="projects" 
        :to="{ name: 'Projects' }"
        active-class="text-primary"
      />
      
      <v-list-item 
        prepend-icon="mdi-account-cog-outline" 
        title="Perfil y Ajustes" 
        value="profile" 
        :to="{ name: 'Profile' }"
        active-class="text-primary"
      />
      
      <v-divider class="my-3"></v-divider>

      <v-list-item 
        prepend-icon="mdi-logout" 
        title="Log out" 
        value="logout" 
        @click="auth.logout"
        class="text-red-lighten-2"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
// Nota: La redirección a /login tras logout ya está en el store auth.ts
</script>