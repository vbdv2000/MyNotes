import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
    withCredentials: false,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    response => response,
    error => {
        // Solo actuar si el error es 401
        if (error.response && error.response.status === 401) {
            console.error("401 Unauthorized. Redirecting to login.");
            localStorage.removeItem('access_token');
            router.push({ name: 'Login' });
        }
        return Promise.reject(error); 
    }
);

export default api;