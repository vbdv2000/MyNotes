<template>
  <v-card 
    class="mb-3 pa-2 task-card"
    :color="cardBgColor" 
    :style="{ 
        borderLeft: `5px solid ${priorityBorderColor}`, 
        boxShadow: priorityShadow 
    }"
    @click="$emit('editTask', task.id)"
  >
    <v-card-text class="py-1 px-2">
      <div class="d-flex justify-space-between align-start mb-1">
        
        <v-icon
            :icon="taskPriority.icon"
            :color="taskPriority.color"
            size="small"
            class="me-2 mt-1"
            :title="taskPriority.label"
        />
        
        <div class="text-subtitle-1 font-weight-bold flex-grow-1 text-truncate">
          {{ task.title }}
        </div>
        
        <span class="text-caption text-medium-emphasis ms-2 mt-1">#{{ task.id }}</span>
      </div>

      <div 
        v-if="task.description" 
        class="text-caption mt-1 text-grey-lighten-2 text-truncate-2"
        :title="task.description"
      >
          {{ task.description }}
      </div>
      
      <div v-if="task.due_date" class="text-caption mt-2 d-flex align-center">
        <v-icon size="small" icon="mdi-calendar-range" class="mr-1 text-medium-emphasis" />
        <span class="font-weight-medium">Vence: {{ formattedDueDate }}</span>
      </div>
    </v-card-text>

    <v-divider class="my-2"></v-divider>

    <v-card-actions class="pa-0 d-flex justify-space-between align-center px-2">
      
      <div class="d-flex overflow-x-auto align-center flex-grow-1 tag-list">
        <v-chip
          v-for="tag in task.tags.slice(0, 3)" :key="tag.id"
          size="x-small"
          label
          class="mr-1 font-weight-medium"
          :style="{ 
            backgroundColor: tag.color, 
            color: getContrastColor(tag.color) 
          }" >
          {{ tag.name }}
        </v-chip>
        
        <v-chip 
          v-if="task.tags && task.tags.length > 3" size="x-small" 
          label 
          class="font-weight-medium"
          color="grey-darken-2" >
          +{{ task.tags.length - 3 }}
        </v-chip>
      </div>
      <v-spacer></v-spacer>

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

const priorityMapping = {
    urgent: { color: '#B71C1C', bg_class: 'red-lighten-5', icon: 'mdi-fire', label: 'Urgente' }, 
    high: { color: '#E65100', bg_class: 'orange-lighten-5', icon: 'mdi-alert', label: 'Alta' },  
    medium: { color: '#01579B', bg_class: 'blue-grey-lighten-5', icon: 'mdi-minus', label: 'Media' },
    low: { color: '#1B5E20', bg_class: 'blue-grey-lighten-5', icon: 'mdi-check', label: 'Baja' },
};

const taskPriority = computed(() => priorityMapping[props.task.priority] || priorityMapping.medium);

const cardBgColor = computed(() => {
    return 'grey-darken-4'; 
});

const priorityBorderColor = computed(() => taskPriority.value.color);

const priorityShadow = computed(() => {
    // Definimos los parámetros de la sombra: offset-x | offset-y | blur-radius | spread-radius | color
    // Usamos el color de prioridad, pero lo hacemos más transparente (ej: rgba)
    const color = taskPriority.value.color; // Obtener el color HEX
    
    // Necesitamos convertir HEX a RGB o RGBA para añadir transparencia.
    // Una función utilitaria para HEX a RGBA:
    const hexToRgba = (hex: string, alpha = 1) => {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    // Aplicar la sombra con una transparencia baja
    const shadowColor = hexToRgba(color, 0.2); // 20% de opacidad para la sombra
    return `0px 0px 10px 2px ${shadowColor}`; // Ajusta los valores para el efecto deseado
});

// --- Formato de Fecha ---
const formattedDueDate = computed(() => {
    if (!props.task.due_date) return '';
    const date = new Date(props.task.due_date);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
});

const getContrastColor = (hex: string): string => {
    if (!hex || hex.length !== 7) return 'black';

    // Convertir HEX a valores RGB
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    // Calcular la luminosidad (fórmula YIQ para determinar el contraste)
    // El umbral estándar es 128 o 186. Usaremos 186 para asegurar un buen contraste en un diseño profesional.
    const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
    
    // Si la luminosidad es mayor que 186, el color de fondo es claro -> usar texto negro.
    // De lo contrario, el color de fondo es oscuro -> usar texto blanco.
    return (yiq >= 186) ? 'black' : 'white';
};
</script>

<style scoped>
.task-card {
    box-sizing: border-box; 
    padding-left: 7px !important;
    /* Hacemos la tarjeta más pequeña */
    max-width: 280px; 
    white-space: normal;
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

.tag-list {
    flex-wrap: nowrap; /* Asegura que no salten de línea */
    overflow-x: hidden; /* Oculta la barra de desplazamiento */
    /* Añade un sutil efecto de desvanecimiento si hay muchas tags (opcional) */
}
</style>