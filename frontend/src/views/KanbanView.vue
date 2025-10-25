<template>
  <v-container fluid class="pt-8 kanban-board-container">
    
    <div class="d-flex justify-space-between align-center mb-6">
      <h1 class="text-h4 font-weight-bold">
          {{ taskStore.currentProject?.title || `Project ID: ${projectId}` }}
          <v-btn
            icon="mdi-cog"
            variant="text"
            size="small"
            class="ms-2"
            @click="isEditDialogOpen = true" />
      </h1>
      <v-btn 
        color="primary" 
        prepend-icon="mdi-plus" 
        @click="isCreateDialogOpen = true"
      >
        Add Task
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
    
    <v-dialog
        v-model="isEditDialogOpen"
        :fullscreen="$vuetify.display.xs"
        max-width="800"
    >
        <ProjectEditDialog 
            v-if="isEditDialogOpen"
            :project-id="projectId"
            v-model="isEditDialogOpen"
            @projectUpdated="handleProjectUpdated"
            @close="isEditDialogOpen = false"
        />
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTaskStore, Task } from '@/stores/task';
import KanbanColumn from '@/components/tasks/KanbanColumn.vue';
import TaskCreateDialog from '@/components/tasks/TaskCreateDialog.vue';
import ProjectEditDialog from '@/components/projects/ProjectEditDialog.vue';
import { VRow, VCol, VContainer, VAlert, VSkeletonLoader, VDialog } from 'vuetify/components';

// --- Setup y State ---

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();

// Lee el parámetro 'id' de la ruta (corregido de la conversación anterior)
const projectId = computed(() => Number(route.params.id));
const loading = ref(true);
const error = ref('');
const isCreateDialogOpen = ref(false);
const isEditDialogOpen = ref(false);

// Definición de las columnas del tablero
const statusDefinitions = [
  { key: 'todo', title: 'TO DO' },
  { key: 'in_progress', title: 'IN PROGRESS' },
  { key: 'review', title: 'FOR REVIEW' },
  { key: 'done', title: 'DONE' },
] as const;

// --- Computed Properties ---
// Filtra las tareas para la columna dada
const getTasksByStatus = (statusKey: string): Task[] => {
  // taskStore.tasks es reactivo y siempre se actualizará con los datos del store
  return taskStore.tasks 
    .filter(task => task.status === statusKey)
    // 💡 Opcional: Añadir un sort() aquí si quieres ordenar por 'order'
    .sort((a, b) => (a.order || 0) - (b.order || 0)); 
};

// --- Lifecycle y Data Fetching ---

const fetchProjectData = async () => {
    loading.value = true;
    error.value = '';
    try {
        // Cargar tareas
        await taskStore.fetchTasks(projectId.value); 
        // Cargar detalles del proyecto para el título y el diálogo de edición
        await taskStore.fetchProjectDetails(projectId.value);
    } catch (err) {
        error.value = 'Error al cargar los datos del proyecto.';
        console.error(err);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    if (projectId.value) {
        fetchProjectData();
    }
});

const handleProjectUpdated = () => {
    // 1. Cerrar el diálogo
    isEditDialogOpen.value = false;
    // 2. Recargar los detalles del proyecto para actualizar el título/UI
    taskStore.fetchProjectDetails(projectId.value);
    // Nota: El ProjectEditDialog ya ha guardado los cambios en el store (tags, colaboradores).
};


// --- Lógica de Interacción ---

/**
 * Maneja el movimiento de una tarea entre columnas (Drag & Drop).
 */
const handleTaskMove = async ({ taskId, newStatus }: { taskId: number, newStatus: typeof statusDefinitions[number]['key'] }) => {
  try {
    // 1. Optimistic UI Update: Actualizar localmente el estado del store
    const task = taskStore.tasks.find(t => t.id === taskId);
    if (task) {
        task.status = newStatus;
    }

    // 2. Llamada al Store para persistir el cambio
    await taskStore.updateTaskStatus(projectId.value, taskId, newStatus);
    
  } catch (err) {
    error.value = 'Error al mover la tarea.';
    console.error(err);
    // 3. Revertir la UI forzando una recarga si la llamada falla
    fetchProjectData(); 
  }
};

/**
 * Maneja el reordenamiento de tareas dentro de una columna.
 */
const handleTaskReorder = async (statusKey: typeof statusDefinitions[number]['key'], updatedList: Task[]) => {
    // Lógica para actualizar el orden en el backend
    const newOrder = updatedList.map((task, index) => ({ id: task.id, order: index }));
    
    // 💡 Aquí necesitarías llamar a una acción en el store:
    // await taskStore.updateTaskOrder(statusKey, newOrder);
};


/**
 * Redirige al usuario a la vista de edición avanzada de la tarea.
 */
const handleEditTask = (taskId: number) => {
  router.push({ 
    name: 'TaskEdit',
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
  fetchProjectData(); 
};

</script>

<style scoped>
.kanban-board-container {
  max-width: none; 
}
.kanban-board-row {
  flex-wrap: nowrap;
  overflow-x: auto;
  min-height: 70vh;
  padding-bottom: 20px;
}
.kanban-board-row::-webkit-scrollbar {
    height: 8px; 
}
.kanban-board-row::-webkit-scrollbar-thumb {
    background-color: #888;
    border-radius: 4px;
}
</style>