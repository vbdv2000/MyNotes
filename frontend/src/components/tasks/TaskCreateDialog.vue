<template>
  <v-card>
    <v-card-title class="text-h5 primary-title">Crear Nueva Tarea</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="submitTask">
        
        <v-text-field 
          v-model="newTask.title" 
          label="Título de la Tarea" 
          :rules="[v => !!v || 'El título es obligatorio']" 
          required 
          class="mb-3"
        />

        <v-textarea 
          v-model="newTask.description" 
          label="Descripción" 
          rows="3" 
          class="mb-3"
        />

        <v-select
          v-model="newTask.priority"
          :items="priorityOptions"
          label="Prioridad"
          required
          class="mb-3"
        />

        <v-select
          v-model="newTask.assigned_user_id"
          :items="[]"
          label="Asignar a (Opcional)"
          placeholder="Selecciona un miembro del equipo"
          clearable
        />

        <v-alert v-if="error" type="error" class="mt-4">{{ error }}</v-alert>

        <v-card-actions class="pa-0 mt-4">
          <v-spacer></v-spacer>
          <v-btn 
            variant="text" 
            @click="emit('close')"
          >
            Cancelar
          </v-btn>
          <v-btn 
            type="submit" 
            color="primary" 
            :loading="loading"
            :disabled="!newTask.title"
            variant="flat"
          >
            Crear Tarea
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useTaskStore, Task } from '@/stores/task'; // Asegúrate de la importación
import { VCard, VCardTitle, VCardText, VForm, VTextField, VTextarea, VSelect, VAlert, VCardActions, VSpacer } from 'vuetify/components';

// Definición de Props y Emits
const props = defineProps<{
    projectId: number;
}>();

const emit = defineEmits(['taskCreated', 'close']);

// --- Store y Estado ---
const taskStore = useTaskStore();
const loading = ref(false);
const error = ref('');

// Estructura inicial de la nueva tarea
const newTask = ref({
    title: '',
    description: '',
    priority: 'medium', // Valor por defecto
    assigned_user_id: null as number | null,
    // El status (todo) y el project_id se añaden en submitTask
});

const priorityOptions = [
    { title: 'Urgente', value: 'urgent' },
    { title: 'Alta', value: 'high' },
    { title: 'Media', value: 'medium' },
    { title: 'Baja', value: 'low' },
];

// --- Lógica de Creación ---
const submitTask = async () => {
    if (!newTask.value.title) return;

    loading.value = true;
    error.value = '';

    // Datos que se enviarán al Store
    const payload = {
        ...newTask.value,
        project_id: props.projectId,
        status: 'todo', // Nueva tarea siempre empieza en TO DO
    };

    try {
        // 💡 Llama a la acción del store para crear la tarea
        const createdTask: Task = await taskStore.createTask(payload);

        // Notifica a KanbanView.vue que la tarea fue creada y cierra el diálogo
        emit('taskCreated', createdTask);
        
        // Resetear el formulario
        newTask.value = {
            title: '',
            description: '',
            priority: 'medium',
            assigned_user_id: null,
        };

    } catch (err) {
        error.value = 'No se pudo crear la tarea. Inténtalo de nuevo.';
        console.error(err);
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.primary-title {
    background-color: var(--v-theme-primary);
    color: white;
}
</style>