<template>
  <v-dialog
    :fullscreen="$vuetify.display.xs"
    max-width="600"
    transition="dialog-bottom-transition"
    scrollable
  >
    <v-card>
      <v-card-title class="text-h5 primary-title d-flex align-center">
        Create New Task
        <v-spacer v-if="$vuetify.display.xs"></v-spacer>
        <v-btn v-if="$vuetify.display.xs" icon="mdi-close" variant="text" @click="emit('close')"></v-btn>
      </v-card-title>
      
      <v-card-text>
        <v-container fluid class="pa-0">
          <v-form @submit.prevent="submitTask">
            
            <v-text-field 
              v-model="newTask.title" 
              label="Task Title" 
              :rules="[v => !!v || 'Title is required']" 
              required 
              variant="underlined"
              class="mb-3"
            />

            <v-textarea 
              v-model="newTask.description" 
              label="Task Description" 
              rows="3" 
              variant="outlined"
              class="mb-3"
            />

            <ProjectTagManager
              :project-id="projectId"
              :initial-tag-ids="newTask.tag_ids"
              @update:tags="handleTagUpdate"
            />

            <v-label class="mt-4">Prioridad</v-label>
            <v-btn-toggle
                v-model="newTask.priority"
                color="primary"
                mandatory
                class="mb-3 w-100"
                group
                :density="$vuetify.display.xs ? 'compact' : 'default'"
            >
                <v-btn
                    v-for="p in priorityOptions"
                    :key="p.value"
                    :value="p.value"
                    :color="p.color"
                    class="flex-grow-1"
                >
                    <v-icon :icon="p.icon" class="me-2" size="small"></v-icon>
                    <span v-if="!$vuetify.display.xs">{{ p.title }}</span>
                </v-btn>
            </v-btn-toggle>

            <v-select
              v-model="newTask.assigned_user_id"
              :items="[]"
              label="Assign to (Optional)"
              placeholder="Select a team member"
              clearable
              variant="outlined"
            />

            <v-alert v-if="error" type="error" class="mt-4">{{ error }}</v-alert>

            <v-card-actions class="pa-0 mt-4">
              <v-spacer></v-spacer>
              <v-btn 
                variant="text" 
                @click="emit('close')"
              >
                Cancel
              </v-btn>
              <v-btn 
                type="submit" 
                color="primary" 
                :loading="loading"
                :disabled="!newTask.title"
                variant="flat"
              >
                Create Task
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'; // 💡 Importar onMounted
import { useTaskStore, Task } from '@/stores/task';
import ProjectTagManager from '@/components/tags/ProjectTagManager.vue';
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