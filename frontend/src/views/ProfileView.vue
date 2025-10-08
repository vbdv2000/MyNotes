<template>
  <v-container>
    <v-card class="mx-auto" max-width="600" title="Información Personal">
      
      <v-card-text v-if="authStore.user">
        <v-list density="compact">
          <v-list-item prepend-icon="mdi-account" :title="authStore.user.full_name" subtitle="Nombre Completo"></v-list-item>
          <v-list-item prepend-icon="mdi-email" :title="authStore.user.email" subtitle="Email"></v-list-item>
          <v-divider></v-divider>
          <v-list-item prepend-icon="mdi-identifier" :title="authStore.user.id.toString()" subtitle="ID de Usuario"></v-list-item>
        </v-list>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red-darken-1" @click="authStore.logout" prepend-icon="mdi-logout">Cerrar Sesión</v-btn>
      </v-card-actions>

      <v-skeleton-loader v-if="authStore.loading && !authStore.user" type="list-item-two-line, divider, list-item-two-line"></v-skeleton-loader>
      <v-alert v-if="!authStore.user && !authStore.loading" type="info">Cargando datos del usuario...</v-alert>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import { onMounted } from 'vue';

const authStore = useAuthStore();

onMounted(() => {
    if (!authStore.user) {
        authStore.fetchUser();
    }
});
</script>