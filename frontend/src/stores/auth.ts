import { defineStore } from "pinia";
import api from "@/api/axios";
import { jwtDecode } from "jwt-decode";

interface FastAPIValidationError {
    type: string;
    loc: (string | number)[];
    msg: string;
    input: any;
    ctx?: any;
}

function handleApiError(err: any): string {
    const responseData = err.response?.data;

    if (responseData && Array.isArray(responseData.detail) && responseData.detail.length > 0) {
        const firstError = responseData.detail[0] as FastAPIValidationError;

        let cleanMsg = firstError.msg.replace("Value error, ", "");

        const field = firstError.loc?.[1] || 'un campo';

        return `Error en ${field}: ${cleanMsg}`;
    }


    if (responseData?.detail) {
        if (typeof responseData.detail === 'string') {
            return responseData.detail;
        }
    }

    return "Error de conexión o fallo desconocido en el servidor.";
}

export const useAuthStore = defineStore("auth", {
    state: () => ({
        token: localStorage.getItem("token") || "",
        user: null as null | { id: number; email: string; full_name: string },
        loading: false,
        error: null,
    }),
    actions: {
        async login(email: string, password: string) {
            this.loading = true;
            this.error = null;
            try {
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);

                const res = await api.post("/auth/login", formData, {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                });
                this.token = res.data.access_token;
                localStorage.setItem("token", this.token);
                const decodedToken = jwtDecode<{ user_id: string }>(this.token);
                this.currentUserId = decodedToken.user_id;
                localStorage.setItem("user_id", this.currentUserId);

                await this.fetchUser();
                return true;
            } catch (err: any) {
                this.error = err.response?.data?.detail || "Login failed";
                return false;
            } finally {
                this.loading = false;
            }
        },
        async register(email: string, password: string, full_name: string) {
            this.loading = true;
            this.error = null;
            try {
                await api.post("/users/", {
                    email,
                    password,
                    full_name,
                });
                // Auto-login after register
                await this.login(email, password);
                return true;
            } catch (err: any) {
                this.error = handleApiError(err);
                return false;
            } finally {
                this.loading = false;
            }
        },
        async fetchUser() {
            if (!this.token) return;
            try {
                const res = await api.get(`/users/${this.currentUserId}`);

                this.user = res.data;
            } catch {
                this.logout();
            }
        },
        logout() {
            this.token = "";
            this.user = null;
            localStorage.removeItem("token");
        },
    },
});