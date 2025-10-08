<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card color="surface">
      <v-card-title class="text-h6 text-primary">
        Quick Task Creation
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="saveTask">
          <v-text-field
            v-model="title"
            label="Task Title"
            variant="outlined"
            required
            :rules="[v => !!v || 'Title is required']"
            class="mb-3"
            autofocus
          />
          
          <v-select
            v-model="status"
            :items="statusOptions"
            item-title="title"
            item-value="key"
            label="Column (Status)"
            variant="outlined"
            density="compact"
            class="mb-3"
          />
          
          <v-alert v-if="error" type="error" class="mb-3" dense>{{ error }}</v-alert>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red-lighten-2" variant="text" @click="dialog = false">Cancel</v-btn>
            <v-btn color="primary" type="submit" :loading="loading" class="text-black">Create Task</v-btn>
          </v-card-actions>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useTaskStore } from '@/stores/task'; // Asumimos este store

const props = defineProps<{
  projectId: number;
}>();

const emit = defineEmits(['task-created']);

const taskStore = useTaskStore();
const dialog = ref(false);
const title = ref('');
const status = ref('todo');
const loading = ref(false);
const error = ref<string | null>(null);

const statusOptions = [
  { key: 'todo', title: 'Pendiente' },
  { key: 'in_progress', title: 'En Progreso' },
  { key: 'review', title: 'Revisión' },
  { key: 'done', title: 'Completado' },
];

const open = (initialStatus: string = 'todo') => {
  title.value = '';
  status.value = initialStatus;
  error.value = null;
  dialog.value = true;
};

const saveTask = async () => {
  if (!title.value) return; 

  loading.value = true;
  error.value = null;

  try {
    // API Call: POST /api/projects/{project_id}/tasks
    await taskStore.createTask(props.projectId, { 
      title: title.value, 
      status: status.value 
      // Aquí se podría añadir descripción, fecha, etc., para una edición más completa.
    }); 
    
    emit('task-created');
    dialog.value = false;
  } catch (e: any) {
    error.value = e.message || "Fallo al crear la tarea.";
  } finally {
    loading.value = false;
  }
};

defineExpose({
  open,
});
</script>