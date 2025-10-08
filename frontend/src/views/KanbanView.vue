<template>
  <v-container fluid class="pt-8 kanban-board-container">
    
    <div class="d-flex justify-space-between align-center mb-6">
      <h1 class="text-h4 font-weight-bold">
        Tablero Kanban (Proyecto ID: {{ projectId }})
      </h1>
      <v-btn 
        color="primary" 
        prepend-icon="mdi-plus" 
        @click="isCreateDialogOpen = true"
      >
        Añadir Tarea
      </v-btn>
    </div>

    <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
    <v-skeleton-loader v-if="loading" type="card, card, card" :loading="loading" class="mb-4"></v-skeleton-loader>

    <v-row v-else class="kanban-board-row">
      
      <v-col
        v-for="statusDef in statusDefinitions"
        :key="statusDef.key"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <KanbanColumn
          :title="statusDef.title"
          :status-key="statusDef.key"
          :tasks="getTasksByStatus(statusDef.key)"
          
          @taskMoved="handleTaskMove"
          @addTask="isCreateDialogOpen = true"
          @editTask="handleEditTask"
          
          @update:tasks="handleTaskReorder(statusDef.key, $event)"
        />
      </v-col>
    </v-row>

    <v-dialog 
      v-model="isCreateDialogOpen" 
      max-width="600"
    >
        <TaskCreateDialog 
            :project-id="projectId"
            @taskCreated="handleTaskCreated"
            @close="isCreateDialogOpen = false"
        />
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTaskStore, Task } from '@/stores/task'; // Asegúrate de que 'Task' se exporta desde tu store
import KanbanColumn from '@/components/tasks/KanbanColumn.vue';
import TaskCreateDialog from '@/components/tasks/TaskCreateDialog.vue'; // Componente que debes crear
import { VRow, VCol, VContainer, VAlert, VSkeletonLoader, VDialog } from 'vuetify/components';

// --- Setup y State ---

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();

const projectId = computed(() => Number(route.params.projectId));
const loading = ref(true);
const error = ref('');
const isCreateDialogOpen = ref(false);

// La lista de todas las tareas del proyecto
const projectTasks = ref<Task[]>([]);

// Definición de las columnas del tablero
const statusDefinitions = [
  { key: 'todo', title: 'TO DO' },
  { key: 'in_progress', title: 'IN PROGRESS' },
  { key: 'review', title: 'FOR REVIEW' },
  { key: 'done', title: 'DONE' },
] as const;

// --- Computed Properties ---

// Filtra las tareas para la columna dada
const getTasksByStatus = (statusKey: typeof statusDefinitions[number]['key']): Task[] => {
  return projectTasks.value
    .filter(task => task.status === statusKey)
    .sort((a, b) => (a.order || 0) - (b.order || 0)); // Asumiendo un campo 'order'
};

// --- Lifecycle y Data Fetching ---

const fetchProjectTasks = async () => {
  loading.value = true;
  error.value = '';
  try {
    // 💡 Llama a la acción del store para obtener las tareas del proyecto
    const tasks = await taskStore.fetchTasks(projectId.value); 
    projectTasks.value = tasks;
  } catch (err) {
    error.value = 'Error al cargar las tareas del proyecto.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (projectId.value) {
    fetchProjectTasks();
  }
});


// --- Lógica de Interacción ---

/**
 * Maneja el movimiento de una tarea entre columnas (Drag & Drop).
 */
const handleTaskMove = async ({ taskId, newStatus }: { taskId: number, newStatus: typeof statusDefinitions[number]['key'] }) => {
  try {
    // 1. Optimistic UI Update: Actualizar localmente antes de la respuesta del servidor
    const taskIndex = projectTasks.value.findIndex(t => t.id === taskId);
    if (taskIndex !== -1) {
        projectTasks.value[taskIndex].status = newStatus;
    }

    // 2. Llamada al Store para persistir el cambio
    await taskStore.updateTaskStatus(taskId, newStatus);
    
  } catch (err) {
    error.value = 'Error al mover la tarea.';
    console.error(err);
    // 3. Revertir la UI si la llamada falla (Opcional, pero recomendado)
    fetchProjectTasks(); 
  }
};

/**
 * Maneja el reordenamiento de tareas dentro de una columna.
 */
const handleTaskReorder = async (statusKey: typeof statusDefinitions[number]['key'], updatedList: Task[]) => {
    // Reemplaza la lista de tareas local solo para esa columna (lo hace v-model)
    // El orden de los elementos en updatedList ya refleja el nuevo orden en la UI.
    
    // 💡 Aquí implementarías la lógica para actualizar el campo 'order' en tu backend
    // 1. Obtener los IDs y el nuevo orden
    const newOrder = updatedList.map((task, index) => ({ id: task.id, order: index }));
    
    // 2. Llamada al Store (Función que debes implementar: updateTaskOrder)
    // await taskStore.updateTaskOrder(statusKey, newOrder);
};


/**
 * Redirige al usuario a la vista de edición avanzada de la tarea.
 */
const handleEditTask = (taskId: number) => {
  router.push({ 
    name: 'TaskEdit', // 💡 Asegúrate de que esta ruta esté definida en tu router
    params: { 
        projectId: projectId.value, 
        taskId: taskId 
    } 
  });
};

/**
 * Se llama cuando TaskCreateDialog ha creado una tarea con éxito.
 */
const handleTaskCreated = () => {
  isCreateDialogOpen.value = false;
  fetchProjectTasks(); // Recarga la lista completa para mostrar la nueva tarea
};

</script>

<style scoped>
.kanban-board-container {
  /* Permite que el contenido se estire más allá del ancho estándar de v-container */
  max-width: none; 
}
.kanban-board-row {
  /* Asegura que las columnas floten y no tengan saltos de línea innecesarios */
  flex-wrap: nowrap;
  overflow-x: auto;
  min-height: 70vh;
  padding-bottom: 20px;
}
/* Estilo para navegadores basados en Webkit (Chrome, Safari) */
.kanban-board-row::-webkit-scrollbar {
    height: 8px; 
}
.kanban-board-row::-webkit-scrollbar-thumb {
    background-color: #888;
    border-radius: 4px;
}
</style>