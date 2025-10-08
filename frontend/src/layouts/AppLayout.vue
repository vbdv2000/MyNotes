<template>
  <v-app>
    <AppDrawer />

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import AppDrawer from '@/components/AppDrawer.vue';
</script>