<template>
  <v-card class="pa-3 elevation-5 column-card" color="surface">
    
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 :class="['text-subtitle-1', 'font-weight-bold', statusColorClass]">
        {{ title }}
      </h2>
      <v-chip size="small" variant="flat" :color="statusChipColor" class="text-black">
        {{ tasks.length }}
      </v-chip>
    </div>

    <draggable
      class="task-list"
      v-model="tasks"
      group="tasks"
      item-key="id"
      @change="onTaskChange"
    >
      <template #item="{ element }">
        <div class="mb-3">
          <TaskCard 
            :task="element" 
            @click="emit('editTask', element.id)" 
          />
        </div>
      </template>
      
      <template #footer>
        <div v-if="tasks.length === 0" class="text-caption text-center pt-4 text-medium-emphasis">
            Arrastra tareas aquí o haz clic en "Nueva Tarea"
        </div>
      </template>
    </draggable>

    <v-btn
        block
        variant="text"
        color="primary"
        prepend-icon="mdi-plus"
        size="small"
        class="mt-2"
        @click="$emit('addTask')"
    >
        New Task
    </v-btn>

  </v-card>
</template>

<script setup lang="ts">
// 💡 LIBRERÍA CORRECTA PARA VUE 3
import draggable from 'vuedraggable'
import { computed, watch } from 'vue';
import { Task } from '@/stores/task'; 
import TaskCard from '@/components/tasks/TaskCard.vue'; 

const props = defineProps<{
  title: string;
  statusKey: 'todo' | 'in_progress' | 'review' | 'done';
  tasks: Task[];
}>();

const emit = defineEmits(['taskMoved', 'addTask', 'editTask', 'update:tasks']);

// 💡 NECESARIO: Ya que usamos v-model en VueDraggable, necesitamos un getter/setter
const tasks = computed({
  get: () => props.tasks,
  set: (value) => {
    // Cuando VueDraggable actualiza la lista internamente
    emit('update:tasks', value); 
  }
});

// --- Colores y estilos ---
const statusChipColor = computed(() => {
    switch (props.statusKey) {
        case 'todo': return 'blue-grey-lighten-1';
        case 'in_progress': return 'primary'; 
        case 'review': return 'orange-lighten-1';
        case 'done': return 'green-lighten-1';
        default: return 'grey-lighten-1';
    }
});
const statusColorClass = computed(() => `text-${statusChipColor.value}`);

// --- Lógica Drag & Drop ---
const onTaskChange = (event: { added?: { element: Task, newIndex: number }, removed?: any, moved?: any }) => {
    // Este evento se dispara cuando una tarea es SOLTADA en esta columna (añadida)
    if (event.added) {
        const taskId = event.added.element.id;
        const newStatus = props.statusKey;
        
        // Emitimos el evento a KanbanView.vue para que el store actualice el backend
        emit('taskMoved', { taskId, newStatus });
    }
};
</script>

<style scoped>
.column-card {
  min-height: 50vh; 
  display: flex;
  flex-direction: column;
}
.task-list {
  flex-grow: 1; 
  overflow-y: auto; 
  min-height: 50px; 
  padding-right: 5px;
}
</style>