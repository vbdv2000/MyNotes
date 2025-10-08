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
        prepend-icon="mdi-view-column" 
        title="Projects" 
        value="projects" 
        :to="{ name: 'Projects' }"
        active-class="text-primary"
      />
      
      <v-list-item 
        prepend-icon="mdi-bell-outline" 
        title="Notifications" 
        value="notifications" 
        :to="{ name: 'Notifications' }"
        active-class="text-primary"
      />
      
      <v-divider class="my-3"></v-divider>

      <v-list-item 
        prepend-icon="mdi-tag-multiple-outline" 
        title="Tags Management" 
        value="tags" 
        :to="{ name: 'Tags' }"
        active-class="text-primary"
      />
      <v-list-item 
        prepend-icon="mdi-account-cog-outline" 
        title="Settings" 
        value="profile" 
        :to="{ name: 'Profile' }"
        active-class="text-primary"
      />
      
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
</script>