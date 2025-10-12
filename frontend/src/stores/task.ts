// src/stores/task.ts
import { defineStore } from "pinia";
import api from "@/api/axios";

// --- Tipos Basados en el Backend ---
interface User { id: number; email: string; full_name: string; }
interface Tag { id: number; name: string; color: string; }

export interface Task {
    id: number;
    title: string;
    description: string | null;
    status: 'todo' | 'in_progress' | 'review' | 'done';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    project_id: number;
    assigned_users: User[];
    tags: Tag[];
    created_at: string;
}

interface TaskCreationData {
    title: string;
    description?: string;
    priority: Task['priority'];
    status: Task['status'];
    project_id: number;
    assigned_user_id?: number | null;
    tag_ids?: number[];
}

export interface Project {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
    tasks_count: number;
    created_at: string;
}

// --- Store de Tareas y Proyectos ---
export const useTaskStore = defineStore("task", {
    state: () => ({
        projects: [] as Project[],
        tasks: [] as Task[],
        projectTags: [] as Tag[],
        currentProject: null as Project | null,
        loading: false,
        error: null as string | null,
    }),
    actions: {
        async fetchProjects() {
            this.loading = true;
            try {
                // API: GET /api/projects/
                const res = await api.get('/projects/');
                this.projects = res.data;
            } catch (err: any) {
                this.error = "Error al cargar los proyectos.";
            } finally {
                this.loading = false;
            }
        },

        async createProject(title: string, description?: string) {
            this.loading = true;
            try {
                // API: POST /api/projects/
                await api.post('/projects/', { title, description });
                await this.fetchProjects();
            } catch (err: any) {
                this.error = "Error al crear el proyecto.";
            } finally {
                this.loading = false;
            }
        },

        async fetchTasks(projectId: number) {
            this.loading = true;
            try {
                // API: GET /api/projects/{project_id}/tasks
                const res = await api.get(`/projects/${projectId}/tasks`);
                this.tasks = res.data;
            } catch (err: any) {
                this.error = "Error al cargar las tareas.";
            } finally {
                this.loading = false;
            }
        },

        async createTask(data: TaskCreationData) {
            const projectId = data.project_id;
            const res = await api.post(`/projects/${projectId}/tasks`, data);
            await this.fetchTasks(projectId);

            return res.data;
        },

        // Acción clave para el Kanban (simulando Drag & Drop)
        async updateTaskStatus(projectId: number, taskId: number, newStatus: Task['status']) {
            try {
                // API: PUT /api/projects/{project_id}/tasks/{task_id} (o PATCH)
                // Asumimos que el backend puede manejar una actualización de estado simple
                await api.put(`/projects/${projectId}/tasks/${taskId}`, { status: newStatus });

                // Actualización optimista del estado local para fluidez
                const task = this.tasks.find(t => t.id === taskId);
                if (task) {
                    task.status = newStatus;
                }
            } catch (err) {
                // Si falla, podrías revertir el cambio local o forzar una recarga
                console.error("Fallo al actualizar el estado de la tarea", err);
                this.error = "No se pudo cambiar el estado de la tarea.";
            }
        },

        async fetchProjectDetails(projectId: number) {
            try {
                // API: GET /api/projects/{project_id}
                const res = await api.get(`/projects/${projectId}`);
                this.currentProject = res.data;
            } catch (err) {
                this.error = "Proyecto no encontrado.";
            }
        },

        async fetchProjectTags(projectId: number) {
            try {
                const res = await api.get(`/projects/${projectId}/tags`);
                this.projectTags = res.data;
                return res.data;
            } catch (err: any) {
                console.error('Error al cargar tags del proyecto:', err);
                this.error = "Error al cargar las etiquetas del proyecto.";
                return [];
            }
        },
    },
});