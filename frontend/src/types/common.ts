// src/types/common.ts

/** Interfaz base para los usuarios */
export interface User {
    id: number;
    email: string;
    full_name: string;
    // Añade más campos si los tienes (ej: role)
}

/** Interfaz base para las etiquetas */
export interface Tag {
    id: number;
    name: string;
    color: string;
}