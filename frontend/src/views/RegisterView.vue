// RegisterView.vue
<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12 pa-4" color="surface"> <v-card-title class="text-h5 font-weight-bold text-center text-primary mb-4">
            Crea tu Cuenta
          </v-card-title>
          <v-card-text>
            <v-form @submit.prevent="onRegister">
              <v-text-field 
                v-model="full_name" 
                label="Nombre completo" 
                prepend-inner-icon="mdi-account"
                required 
                variant="outlined"
                density="comfortable"
                class="mb-3"
              />
              <v-text-field 
                v-model="email" 
                label="Email" 
                type="email" 
                prepend-inner-icon="mdi-email"
                required 
                variant="outlined"
                density="comfortable"
                class="mb-3"
              />
              <v-text-field 
                v-model="password" 
                label="Contraseña" 
                type="password" 
                prepend-inner-icon="mdi-lock"
                required 
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
              <v-btn 
                :loading="auth.loading" 
                type="submit" 
                color="primary" 
                size="large"
                block 
                class="text-black"
              >
                Registrarse
              </v-btn>
              <v-alert v-if="auth.error" type="error" class="mt-4">{{ auth.error }}</v-alert>
            </v-form>
            <div class="mt-4 text-center">
              <span class="text-white-darken-1">¿Ya tienes cuenta?</span>
              <router-link to="/login" class="text-primary ml-1 font-weight-medium">Inicia sesión</router-link>
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