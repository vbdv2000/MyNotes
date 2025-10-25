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
        Editar Proyecto: {{ editableProject.title || 'Cargando...' }}
        
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
                  label="Título del Proyecto" 
                  :rules="[v => !!v || 'El título es obligatorio']" 
                  variant="outlined"
                  required 
                  class="mb-3"
                />
                
                <v-textarea 
                  v-model="editableProject.description" 
                  label="Descripción Detallada" 
                  rows="4" 
                  variant="outlined"
                  class="mb-3"
                />

                <v-list-item density="compact" class="px-0">
                    <v-list-item-title class="text-subtitle-2">
                        Creado: {{ formattedDate(editableProject.created_at) }}
                    </v-list-item-title>
                </v-list-item>
                <v-list-item density="compact" class="px-0">
                    <v-list-item-title class="text-subtitle-2">
                        Última Edición: {{ formattedDate(editableProject.updated_at) }}
                    </v-list-item-title>
                </v-list-item>

              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="collaboratorIds"
                  :items="[]" item-title="full_name"
                  item-value="id"
                  label="Colaboradores del Proyecto (Temporalmente deshabilitado)"
                  multiple
                  chips
                  variant="outlined"
                  placeholder="Añadir miembros del equipo"
                  class="mb-5"
                  disabled >
                   <template v-slot:chip="{ props }">
                       <v-chip v-bind="props" color="grey-lighten-2" size="small">...</v-chip>
                   </template>
                </v-select>
                
                <v-alert density="compact" type="info" class="mb-5">
                    La gestión de usuarios está temporalmente deshabilitada.
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
              <v-btn variant="text" @click="closeDialog" :disabled="loading">Cancelar</v-btn>
              <v-btn type="submit" color="primary" :loading="loading" variant="flat">
                Guardar Cambios
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
import { useTaskStore } from '@/stores/task'; // O tu store de Proyectos
// 💡 Asumimos que tienes un store de usuarios (userStore) o que usas un composable para ellos
// import { useUserStore } from '@/stores/user'; 
import ProjectTagManager from '@/components/tags/ProjectTagManager.vue'; 
import type { Project, ProjectUpdate } from '@/types/project'; // Asume estos tipos

const props = defineProps<{
    projectId: number;
    modelValue: boolean; // Para controlar el diálogo
}>();

const emit = defineEmits(['update:modelValue', 'projectUpdated', 'close']);

const taskStore = useTaskStore();
// const userStore = useUserStore(); // Asume la existencia del userStore
const loading = ref(false);
const error = ref('');

// Estado inicial (usar un valor dummy para evitar errores al inicio)
const emptyProject: Project = { 
    id: 0, title: '', description: '', owner_id: 0,
    created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    collaborators: [], tags: [], tasks: [], history: [], notifications: []
};
const editableProject = ref<Project>(emptyProject);
const collaboratorIds = ref<number[]>([]);
const tagIds = ref<number[]>([]); 


// --- Handlers de Carga y Sincronización ---

// Carga los detalles del proyecto
const loadProjectDetails = async (id: number) => {
    if (!id || loading.value) return;
    loading.value = true;
    error.value = '';
    try {
        // 💡 Llama a GET /api/projects/{project_id}
        const project: Project = await taskStore.fetchProjectDetails(id); 

        // Inicializa el estado local
        editableProject.value = project;
        collaboratorIds.value = project.collaborators.map(c => c.id);
        tagIds.value = project.tags.map(t => t.id);
        
        // 💡 Cargar usuarios (si no están ya cargados globalmente)
        // if (!userStore.allUsers.length) {
        //     await userStore.fetchAllUsers();
        // }

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
        loadProjectDetails(props.projectId);
    }
});

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
    // Resetear el estado local si es necesario
    editableProject.value = emptyProject;
    emit('update:modelValue', false);
    emit('close');
};

const saveProject = async () => {
    loading.value = true;
    error.value = '';

    try {
        // Payload para el endpoint PATCH /api/projects/{project_id}
        const payload: ProjectUpdate = {
            title: editableProject.value.title,
            description: editableProject.value.description,
            // 💡 Enviar solo las listas de IDs
            collaborator_ids: collaboratorIds.value,
            tag_ids: tagIds.value,
        };
        
        // Asumiendo una acción en el store que llama al endpoint PATCH
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