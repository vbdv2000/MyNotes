// src/types/project.ts

import type { User } from './common';
import type { Tag } from './common';

/**
 * Define la estructura completa del objeto Project (GET /api/projects/{id})
 */
export interface Project {
    id: number;
    title: string;
    description: string | null;
    owner_id: number;
    tasks_count?: number;
    created_at: string;
    updated_at: string;

    // Relaciones completas (asumiendo que las devuelve el backend)
    collaborators: User[];
    tags: Tag[];
    // Nota: El modelo de backend tenía otras relaciones (tasks, history, notifications)
    // Se omiten aquí si no se necesitan en el frontend.
}

/**
 * Define el payload para actualizar parcialmente el proyecto (PATCH /api/projects/{id})
 */
export interface ProjectUpdate {
    title?: string;
    description?: string | null;
    collaborator_ids?: number[]; // Lista de IDs de usuarios
    tag_ids?: number[];         // Lista de IDs de tags
}