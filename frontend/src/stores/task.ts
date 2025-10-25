// src/stores/task.ts
import { defineStore } from "pinia";
import api from "@/api/axios";
import type { Tag, User } from '@/types/common';
import type { Project, ProjectUpdate } from '@/types/project';
import type { Task, TaskCreationData, TaskUpdatePayload } from '@/types/task';

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
        async fetchProjects(): Promise<void> {
            this.loading = true;
            try {
                // API: GET /api/projects/
                const res = await api.get('/projects/');
                this.projects = res.data;
            } catch (err: any) {
                this.error = "Error al cargar los proyectos.";
                console.error("fetchProjects error:", err);
            } finally {
                this.loading = false;
            }
        },

        async createProject(title: string, description?: string): Promise<void> {
            this.loading = true;
            try {
                // API: POST /api/projects/
                await api.post('/projects/', { title, description });
                await this.fetchProjects();
            } catch (err: any) {
                this.error = "Error al crear el proyecto.";
                console.error("createProject error:", err);
            } finally {
                this.loading = false;
            }
        },
        async fetchProjectDetails(projectId: number): Promise<Project | null> {
            this.error = null;
            try {
                // API: GET /api/projects/{project_id}
                const res = await api.get(`/projects/${projectId}`);
                this.currentProject = res.data;

                return res.data;
            } catch (err) {
                this.error = "Proyecto no encontrado o error de carga.";
                console.error("fetchProjectDetails error:", err);
                return null; // 💡 Retorna null si falla
            }
        },

        async updateProject(projectId: number, payload: ProjectUpdate): Promise<Project> {
            this.error = null;
            try {
                // API: PATCH /api/projects/{project_id}
                const response = await api.patch(`/projects/${projectId}`, payload);

                // Opcional: Actualizar la lista de proyectos en el store
                const index = this.projects.findIndex(p => p.id === projectId);
                if (index !== -1) {
                    this.projects[index] = response.data;
                }

                return response.data;
            } catch (err) {
                this.error = "Error al actualizar el proyecto.";
                console.error("updateProject error:", err);
                // 💡 Lanza el error para que el componente lo maneje (ej: mostrar error.value)
                throw err;
            }
        },
        // ------------------------------------------------------------------
        //  TASKS
        // ------------------------------------------------------------------
        async fetchTasks(projectId: number): Promise<void> { // 💡 Añadida tipado de retorno
            this.loading = true;
            this.error = null;
            try {
                // API: GET /api/projects/{project_id}/tasks
                const res = await api.get(`/projects/${projectId}/tasks`);
                this.tasks = res.data;
            } catch (err) {
                this.error = "Error al cargar las tareas.";
                console.error("fetchTasks error:", err);
            } finally {
                this.loading = false;
            }
        },

        async createTask(data: TaskCreationData): Promise<Task> { // 💡 Añadida tipado de retorno
            const projectId = data.project_id;
            this.error = null;
            try {
                // API: POST /api/projects/{project_id}/tasks
                const res = await api.post(`/projects/${projectId}/tasks`, data);

                // 💡 Actualiza la lista sin recargar todas las tareas
                this.tasks.push(res.data);

                return res.data;
            } catch (err) {
                this.error = "Error al crear la tarea.";
                console.error("createTask error:", err);
                throw err;
            }
        },

        // Acción clave para el Kanban (Drag & Drop)
        async updateTaskStatus(projectId: number, taskId: number, newStatus: Task['status']): Promise<void> {
            this.error = null;
            try {
                // 1. Actualización optimista del estado local
                const task = this.tasks.find(t => t.id === taskId);
                if (task) {
                    const oldStatus = task.status;
                    task.status = newStatus;

                    // 2. Determinar projectId a partir de la tarea (si se usa el endpoint simplificado)
                    const projectId = task.project_id;

                    // 3. Llamada al backend
                    await api.patch(`/projects/${projectId}/tasks/${taskId}`, { status: newStatus });

                    // 4. No hay catch, por lo que el optimista se mantiene
                }
            } catch (err) {
                // 💡 Manejo de errores de la tarea: Si falla, revertir y notificar
                const taskToRevert = this.tasks.find(t => t.id === taskId);
                if (taskToRevert) {
                    // Aquí se debería revertir el estado (necesitas almacenar el estado anterior)
                    // taskToRevert.status = oldStatus; 
                }
                console.error("Fallo al actualizar el estado de la tarea", err);
                this.error = "No se pudo cambiar el estado de la tarea.";
                throw err;
            }
        },

        // ------------------------------------------------------------------
        //  TAGS
        // ------------------------------------------------------------------
        async fetchProjectTags(projectId: number): Promise<Tag[]> {
            this.error = null;
            try {
                // API: GET /api/projects/{project_id}/tags
                const res = await api.get(`/projects/${projectId}/tags`);
                this.projectTags = res.data;
                return res.data;
            } catch (err) {
                this.error = "Error al cargar las etiquetas del proyecto.";
                console.error('fetchProjectTags error:', err);
                return [];
            }
        },

        async createProjectTag(projectId: number, tagData: { name: string, color: string }): Promise<Tag> {
            this.error = null;
            try {
                // API: POST /api/projects/{project_id}/tags
                const response = await api.post(`/projects/${projectId}/tags`, tagData);
                const newTag: Tag = response.data;

                // 💡 Actualizar la lista de tags en el store (para el selector)
                const existingIndex = this.projectTags.findIndex(t => t.id === newTag.id);
                if (existingIndex === -1) {
                    this.projectTags.push(newTag);
                }

                return newTag;
            } catch (err) {
                this.error = "Error al crear y asociar la etiqueta.";
                console.error('createProjectTag error:', err);
                throw err;
            }
        },
    },
});