<!-- filepath: frontend/src/views/RegisterView.vue -->
<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="6" md="4">
        <v-card>
          <v-card-title>Registro</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="onRegister">
              <v-text-field v-model="full_name" label="Nombre completo" required />
              <v-text-field v-model="email" label="Email" type="email" required />
              <v-text-field v-model="password" label="Contraseña" type="password" required />
              <v-btn :loading="auth.loading" type="submit" color="primary" block>Registrarse</v-btn>
              <v-alert v-if="auth.error" type="error" class="mt-2">{{ auth.error }}</v-alert>
            </v-form>
            <div class="mt-2">
              ¿Ya tienes cuenta?
              <router-link to="/login">Inicia sesión</router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const full_name = ref("");
const email = ref("");
const password = ref("");
const auth = useAuthStore();
const router = useRouter();

const onRegister = async () => {
  const ok = await auth.register(email.value, password.value, full_name.value);
  if (ok) router.push("/");
};
</script>