import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
// --- Importaciones de Vuetify y Estilos ---
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

// --- Importación de Iconos MDI ---
import "@mdi/font/css/materialdesignicons.css";

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: "mdi",
    },
    theme: {
        defaultTheme: 'vueDark', // Cambiamos el nombre del tema
        themes: {
            vueDark: {
                dark: true,
                colors: {
                    // --- NUEVOS COLORES AL ESTILO VUE.JS ---
                    background: '#1E1E1E', // Gris muy oscuro, casi negro
                    surface: '#282828',    // Gris oscuro para tarjetas/superficies
                    primary: '#42B883',    // Verde vibrante de Vue.js
                    // Puedes añadir otros colores si los necesitas, ej:
                    secondary: '#607D8B',
                    error: '#FF5252',
                    info: '#2196F3',
                    success: '#4CAF50',
                    warning: '#FFC107',
                    // ------------------------------------
                }
            }
        }
    }
    // ------------------------------------
});

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(vuetify);
app.mount("#app");