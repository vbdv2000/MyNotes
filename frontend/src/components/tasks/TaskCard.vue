<template>
  <v-card 
    class="task-card pa-3 elevation-2" 
    :color="priorityColor" 
    rounded="lg"
    hover
    role="button"
  >
    <div class="d-flex justify-space-between align-start">
      
      <v-card-title class="pa-0 text-subtitle-1 font-weight-bold flex-grow-1 text-truncate">
        {{ task.title }}
      </v-card-title>
      
      <v-chip size="x-small" label class="ml-2" color="blue-grey-lighten-2">
        #{{ task.id }}
      </v-chip>
    </div>

    <v-card-text class="pa-0 mt-2 text-caption text-medium-emphasis">
        <div v-if="task.due_date">
            <v-icon size="small" icon="mdi-calendar-range" class="mr-1" />
            Vence: **{{ formattedDueDate }}**
        </div>
        <div v-if="task.description" class="mt-1">
            {{ task.description.substring(0, 50) }}{{ task.description.length > 50 ? '...' : '' }}
        </div>
    </v-card-text>

    <v-divider class="my-2"></v-divider>

    <v-card-actions class="pa-0 d-flex justify-space-between align-center">
        
        <div class="d-flex overflow-x-auto">
            <v-chip
                v-for="tag in task.tags.slice(0, 2)"
                :key="tag.id"
                size="x-small"
                label
                class="mr-1 text-black"
                :color="tag.color || 'blue-grey-lighten-2'"
            >
                {{ tag.name }}
            </v-chip>
            <v-chip 
                v-if="task.tags.length > 2" 
                size="x-small" 
                label 
                class="text-black"
                color="blue-grey-lighten-3"
            >
                +{{ task.tags.length - 2 }}
            </v-chip>
        </div>
        
        <v-avatar-group size="28" max="3">
            <v-avatar 
                v-for="user in task.assigned_users" 
                :key="user.id" 
                :title="user.full_name"
                color="secondary"
            >
                <span class="text-caption text-white">{{ user.full_name ? user.full_name[0].toUpperCase() : '?' }}</span>
            </v-avatar>
        </v-avatar-group>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Task } from '@/stores/task'; 

const props = defineProps<{
    task: Task;
}>();

// --- Lógica de Prioridad para el color de fondo de la tarjeta ---
const priorityColor = computed(() => {
    switch (props.task.priority) {
        case 'urgent': return 'red-lighten-4';
        case 'high': return 'orange-lighten-4';
        case 'medium': return 'blue-grey-lighten-4';
        case 'low': return 'grey-lighten-3';
        default: return 'white';
    }
});

// --- Formato de Fecha ---
const formattedDueDate = computed(() => {
    if (!props.task.due_date) return '';
    const date = new Date(props.task.due_date);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
});
</script>

<style scoped>
.task-card {
    /* Cursor por defecto cuando se puede arrastrar */
    cursor: grab;
    transition: box-shadow 0.2s, transform 0.2s;
}
.task-card:active {
    cursor: grabbing;
}
.text-truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
/* Nuevo estilo para indicar que es clickable para edición */
.task-card:not(:active):hover {
    cursor: pointer; 
}
</style>