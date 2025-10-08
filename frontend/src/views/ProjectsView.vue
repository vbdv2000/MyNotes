<template>
  <v-container fluid class="pt-8">
    
    <v-row class="mb-6" align="center">
      
      <v-col cols="12" sm="8" class="py-0">
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon icon="mdi-view-column" class="mr-2" />
          My Projects
        </h1>
      </v-col>
      
      <v-col cols="12" sm="4" class="py-0">
        <v-btn 
          color="primary" 
          @click="dialog = true" 
          prepend-icon="mdi-plus" 
          size="large" 
          block class="text-black"
        >
          Create New Project
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-if="taskStore.loading">
    </v-row>

    <v-row v-else>
      <v-col v-for="project in taskStore.projects" :key="project.id" cols="12" sm="6" md="4" lg="3">
        <v-card 
          color="surface" 
          class="pa-4 elevation-5 project-card"
          @click="goToKanban(project.id)"
        >
          <v-card-title class="text-h6 font-weight-bold text-primary">{{ project.title }}</v-card-title>
          <v-card-subtitle class="mt-1">
            <v-icon size="small" icon="mdi-account-circle-outline" class="mr-1" />
            Owner: YOU (ID: {{ project.owner_id }})
          </v-card-subtitle>
          
          <v-card-text>
            {{ project.description || 'No description.' }}
          </v-card-text>

          <v-divider class="my-2"></v-divider>

          <v-card-actions class="d-flex justify-space-between">
            <v-chip color="primary" variant="flat" size="small" class="text-black">
              {{ project.tasks_count }} Tasks
            </v-chip>
            <v-icon icon="mdi-arrow-right" color="primary" />
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="500px">
      <v-card color="surface">
        <v-card-title class="text-h6 text-primary">Create Project</v-card-title>
        <v-card-text>
          <v-text-field v-model="newProjectTitle" label="Project Name" variant="outlined" required class="mb-3" />
          <v-textarea v-model="newProjectDescription" label="Description (Optional)" variant="outlined" rows="3" />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red-lighten-2" variant="text" @click="dialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createProject" :loading="taskStore.loading" class="text-black">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTaskStore } from '@/stores/task';

const taskStore = useTaskStore();
const router = useRouter();

const dialog = ref(false);
const newProjectTitle  = ref('');
const newProjectDescription = ref('');

const goToKanban = (project: { id: number | string }) => {
  router.push({ name: 'ProjectKanban', params: { id } });
};

const createProject = async () => {
  if (newProjectTitle.value) {
    await taskStore.createProject(newProjectTitle.value, newProjectDescription.value);
    dialog.value = false;
    newProjectTitle.value = '';
    newProjectDescription.value = '';
  }
};

onMounted(() => {
  taskStore.fetchProjects();
});
</script>

<style scoped>
.project-card {
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4) !important;
}
</style>