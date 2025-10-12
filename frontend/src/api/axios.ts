import axios from "axios";
import { useAuthStore } from '@/stores/auth'; // 💡 Importar el store de autenticación

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore();

        if (authStore.token) {
            config.headers.Authorization = `Bearer ${authStore.token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);


api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Manejo de errores 401
        if (error.response && error.response.status === 401) {
            console.error('401 Unauthorized. Redirecting to login.');

            const authStore = useAuthStore();
            authStore.logout();
        }
        return Promise.reject(error);
    }
);

export default api;