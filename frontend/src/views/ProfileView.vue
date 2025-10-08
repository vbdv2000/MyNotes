<template>
  <v-container class="pt-10">
    <v-card class="mx-auto elevation-10" max-width="800" color="grey-darken-3">
      <v-card-title class="text-h4 font-weight-bold pa-5 text-green-accent-3">
        Personal Information
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text v-if="auth.user">        
        <v-row dense class="mb-3">
          <v-col cols="12" sm="6">
            <v-card variant="tonal" color="green-accent-3" class="pa-3">
              <div class="text-overline">Full Name</div>
              <div class="text-h6">{{ auth.user.full_name }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6">
            <v-card variant="tonal" color="green-accent-3" class="pa-3">
              <div  class="text-overline">User / Email</div>
              <div class="text-h6">{{ auth.user.email }}</div>
            </v-card>
          </v-col>
        </v-row>
        
        <v-row v-if="auth.user.is_superuser" dense class="mb-4">
          <v-col cols="12">
            <v-alert 
              type="success" 
              color="green-darken-3" 
              icon="mdi-shield-crown" 
              variant="tonal"
              title="Superuser permissions"
            >
              You have superuser permissions and can manage other resources.
            </v-alert>
          </v-col>
        </v-row>
        
        <v-divider class="my-4"></v-divider>

      </v-card-text>
    </v-card>

    <v-skeleton-loader v-if="auth.loading && !auth.user" class="mx-auto mt-10" max-width="800" type="article"></v-skeleton-loader>
  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { onMounted } from "vue";

const auth = useAuthStore();

onMounted(() => {
    if (auth.isAuthenticated && !auth.user) {
        auth.fetchUser();
    }
});
</script>