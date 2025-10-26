<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :fullscreen="$vuetify.display.xs"
    max-width="800"
    transition="dialog-bottom-transition"
    scrollable
  >
    <v-card :loading="loading" class="project-edit-card">
      <v-card-title class="text-h5 primary-title d-flex align-center">
        <v-icon icon="mdi-pencil-box-multiple" class="me-2"></v-icon>
        Edit Project: {{ editableProject.title || 'Loading...' }}
        
        <v-spacer v-if="$vuetify.display.xs"></v-spacer>
        <v-btn v-if="$vuetify.display.xs" icon="mdi-close" variant="text" @click="emit('close')"></v-btn>
      </v-card-title>
      
      <v-card-text class="pt-4">
        <v-container fluid class="pa-0">
          <v-form @submit.prevent="saveProject">
            
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field 
                  v-model="editableProject.title" 
                  label="Title" 
                  :rules="[v => !!v || 'Title is required']" 
                  variant="outlined"
                  required 
                  class="mb-3"
                />
                
                <v-textarea 
                  v-model="editableProject.description" 
                  label="Detailed Description" 
                  rows="4" 
                  variant="outlined"
                  class="mb-3"
                />

                <v-list-item density="compact" class="px-0">
                    <v-list-item-title class="text-subtitle-2">
                        Created: {{ formattedDate(editableProject.created_at) }}
                    </v-list-item-title>
                </v-list-item>
                <v-list-item density="compact" class="px-0">
                    <v-list-item-title class="text-subtitle-2">
                        Last Edited: {{ formattedDate(editableProject.updated_at) }}
                    </v-list-item-title>
                </v-list-item>

              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="collaboratorIds"
                  :items="[]" item-title="full_name"
                  item-value="id"
                  label="Project Collaborators (Temporarily Disabled)"
                  multiple
                  chips
                  variant="outlined"
                  placeholder="Add team members"
                  class="mb-5"
                  disabled >
                   <template v-slot:chip="{ props }">
                       <v-chip v-bind="props" color="grey-lighten-2" size="small">...</v-chip>
                   </template>
                </v-select>
                
                <v-alert density="compact" type="info" class="mb-5">
                    User management is temporarily disabled.
                </v-alert>

                <ProjectTagManager 
                  :project-id="projectId" 
                  :initial-tag-ids="tagIds" 
                  @update:tags="handleTagUpdate"
                />
              </v-col>
            </v-row>
            
            <v-alert v-if="error" type="error" class="mt-4">{{ error }}</v-alert>

            <v-card-actions class="pa-0 mt-6">
              <v-spacer></v-spacer>
              <v-btn variant="text" @click="closeDialog" :disabled="loading">Cancel</v-btn>
              <v-btn type="submit" color="primary" :loading="loading" variant="flat">
                Save Changes
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useTaskStore } from '@/stores/task'; 
// import { useUserStore } from '@/stores/user'; // Asume la existencia del userStore
import ProjectTagManager from '@/components/tags/ProjectTagManager.vue'; 
import type { Project, ProjectUpdate } from '@/types/project'; // Asume estos tipos

const props = defineProps<{
    projectId: number;
    modelValue: boolean; // Para controlar el diálogo
}>();

const emit = defineEmits(['update:modelValue', 'projectUpdated', 'close']);

const taskStore = useTaskStore();
// const userStore = useUserStore(); // Asume comentado/deshabilitado
const loading = ref(false);
const error = ref('');

// Estado inicial (usar un valor dummy para evitar errores al inicio)
const emptyProject: Project = { 
    id: 0, title: '', description: '', owner_id: 0,
    created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    collaborators: [], tags: [], tasks: [], history: [], notifications: []
};
const editableProject = ref<Project>({ ...emptyProject }); // Usamos una copia del template vacío

// 💡 CORRECCIÓN 1: Descomentar y definir el ref para los colaboradores.
const collaboratorIds = ref<number[]>([]); 
const tagIds = ref<number[]>([]); 


// --- Handlers de Carga y Sincronización ---

// Carga los detalles del proyecto
const loadProjectDetails = async (id: number) => {
    // Inicialización al abrir el diálogo
    // 💡 REINICIAMOS: Se usa `emptyProject` para que los campos vacíos no muestren datos de un proyecto anterior
    editableProject.value = { ...emptyProject }; 
    collaboratorIds.value = [];
    tagIds.value = [];

    if (!id || loading.value) return;
    
    loading.value = true;
    error.value = '';
    
    try {
        // 1. Llama a la acción y espera la carga
        await taskStore.fetchProjectDetails(id); 
        
        // 2. Comprobamos si el proyecto se cargó correctamente en el store
        // 💡 Importante: usamos la referencia reactiva o el getter del store
        const project = taskStore.currentProject;

        if (project) {
            // 3. COPIA PROFUNDA: Transferencia de datos exitosa del store al estado local
            editableProject.value = JSON.parse(JSON.stringify(project));
            
            // 4. Inicializa los campos de IDs
            collaboratorIds.value = project.collaborators?.map(c => c.id) || [];
            tagIds.value = project.tags?.map(t => t.id) || [];
            
            // 5. Cargar usuarios (si estuviera habilitado)
            // if (!userStore.allUsers.length) { await userStore.fetchAllUsers(); }
            
        } else {
            // Manejo de caso en que el proyecto no se encuentra
            error.value = 'El proyecto no pudo ser encontrado en el store.';
        }

    } catch (e) {
        error.value = 'Error al cargar los detalles del proyecto.';
        console.error(e);
    } finally {
        loading.value = false;
    }
};

// Sincroniza la apertura del diálogo con la carga de datos
watch(() => props.modelValue, (val) => {
    if (val && props.projectId) {
        // Cuando el diálogo se abre (val=true), cargamos los datos.
        loadProjectDetails(props.projectId);
    }
    if (!val) {
        taskStore.currentProject = null; // Asumiendo que esta acción está permitida o tienes un setter/action para limpiar
    }
}, { immediate: true })

// --- Handlers de Interacción ---

const handleTagUpdate = (newTagIds: number[]) => {
    tagIds.value = newTagIds;
};

const formattedDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('es-ES', { 
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
};

const closeDialog = () => {
    // 💡 CORRECCIÓN 3: Revertir `editableProject` al template vacío ANTES de cerrar
    editableProject.value = { ...emptyProject };
    emit('update:modelValue', false);
    emit('close');
};

const saveProject = async () => {
    loading.value = true;
    error.value = '';
    // ... (El resto de la lógica de guardado es correcta) ...
    try {
        const payload: ProjectUpdate = {
            title: editableProject.value.title,
            description: editableProject.value.description,
            // 💡 Manteniendo la compatibilidad para PATCH
            collaborator_ids: collaboratorIds.value,
            tag_ids: tagIds.value,
        };
        
        await taskStore.updateProject(props.projectId, payload);

        emit('projectUpdated');
        closeDialog();

    } catch (e) {
        error.value = 'Error al guardar los cambios del proyecto.';
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
/* Estilo para el título consistente con el resto de la aplicación */
.primary-title {
    background-color: var(--v-theme-primary);
    color: white;
    padding: 16px 24px;
}

/* Estilos para el selector de colaboradores (mejora visual) */
:deep(.v-chip--avatar) .v-avatar {
    margin-inline-end: 8px !important;
}

/* Diseño de dos columnas en desktop, una columna en móvil (gracias a v-row/v-col) */
</style>