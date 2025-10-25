// src/types/task.ts

import type { User } from './common';
import type { Tag } from './common';

export interface Task {
    id: number;
    title: string;
    description: string | null;
    status: 'todo' | 'in_progress' | 'review' | 'done';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    project_id: number;
    assigned_users: User[]; // Lista completa de usuarios asignados
    tags: Tag[];
    created_at: string;
    // updated_at si lo necesitas
}

export interface TaskCreationData {
    title: string;
    description?: string | null;
    priority: Task['priority'];
    status: Task['status'];
    project_id: number;
    assigned_user_id?: number | null;
    tag_ids?: number[];
}

export interface TaskUpdatePayload {
    status?: Task['status'];
    title?: string;
    description?: string;
    priority?: Task['priority'];
    tag_ids?: number[];
    assigned_user_id?: number | null;
}