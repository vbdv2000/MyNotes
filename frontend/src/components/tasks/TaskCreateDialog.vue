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
          v-model="newTask.tag_ids"
          :items="taskStore.projectTags"
          item-title="name"
          item-value="id"
          label="Tags"
          placeholder="Selecciona etiquetas (Opcional)"
          multiple
          chips
          clearable
          :loading="tagsLoading"
        >
          <template v-slot:chip="{ props, item }">
            <v-chip
              v-bind="props"
              :color="item.raw.color || 'blue-grey-lighten-2'"
              size="small"
              :text="item.raw.name"
              label
              class="text-black"
            ></v-chip>
          </template>
          <template v-slot:item="{ props, item }">
            <v-list-item v-bind="props">
              <v-chip
                :color="item.raw.color || 'blue-grey-lighten-2'"
                size="small"
                :text="item.raw.name"
                class="ms-2 text-black"
                label
              ></v-chip>
            </v-list-item>
          </template>
        </v-select>

        <v-label>Prioridad</v-label>
        <v-btn-toggle
            v-model="newTask.priority"
            color="primary"
            mandatory
            class="mb-3"
            group
        >
            <v-btn
                v-for="p in priorityOptions"
                :key="p.value"
                :value="p.value"
                :color="p.color"
            >
                <v-icon :icon="p.icon" class="me-2"></v-icon>
                {{ p.title }}
            </v-btn>
        </v-btn-toggle>

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
import { ref, onMounted } from 'vue'; // 💡 Importar onMounted
import { useTaskStore, Task } from '@/stores/task'; 
import { VCard, VCardTitle, VCardText, VForm, VTextField, VTextarea, VSelect, VAlert, VCardActions, VSpacer } from 'vuetify/components';

// Definición de Props y Emits
const props = defineProps<{
    projectId: number;
}>();

const emit = defineEmits(['taskCreated', 'close']);

// --- Store y Estado ---
const taskStore = useTaskStore();
const loading = ref(false);
const tagsLoading = ref(false); // 💡 Nuevo estado para la carga de tags
const error = ref('');

// Estructura inicial de la nueva tarea
const newTask = ref({
    title: '',
    description: '',
    priority: 'medium',
    assigned_user_id: null as number | null,
    tag_ids: [] as number[], // 💡 Inicializar el array de tags
});

const priorityOptions = [
    { title: 'Baja', value: 'low', color: 'green', icon: 'mdi-check' },
    { title: 'Media', value: 'medium', color: 'blue', icon: 'mdi-minus' },    
    { title: 'Alta', value: 'high', color: 'orange', icon: 'mdi-alert' },
    { title: 'Urgente', value: 'urgent', color: 'red', icon: 'mdi-fire' },

];

// --- Lifecycle y Carga de Datos ---
onMounted(() => {
    // 💡 Cargar las tags disponibles para este proyecto cuando se monta el diálogo
    fetchTags();
});

const fetchTags = async () => {
    tagsLoading.value = true;
    try {
        await taskStore.fetchProjectTags(props.projectId);
    } catch (e) {
        console.error("No se pudieron cargar las tags.");
    } finally {
        tagsLoading.value = false;
    }
};

// --- Lógica de Creación ---
const submitTask = async () => {
    if (!newTask.value.title) return;

    loading.value = true;
    error.value = '';

    // Datos que se enviarán al Store (INCLUYENDO tag_ids)
    const payload = {
        ...newTask.value,
        project_id: props.projectId,
        status: 'todo' as const, 
        // 💡 tag_ids se incluye automáticamente desde newTask.value
    };

    try {
        const createdTask: Task = await taskStore.createTask(payload);

        emit('taskCreated', createdTask);
        
        // Resetear el formulario (incluyendo tags)
        newTask.value = {
            title: '',
            description: '',
            priority: 'medium',
            assigned_user_id: null,
            tag_ids: [], // Resetear las tags
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