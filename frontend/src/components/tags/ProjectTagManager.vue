<template>
  <v-card class="mb-5" flat>
    <v-card-title class="pa-0 text-subtitle-1 d-flex align-center">
      Tags
      <v-spacer></v-spacer>
      <v-btn
        icon="mdi-refresh"
        variant="text"
        size="small"
        @click="fetchProjectTags"
        :loading="loadingTags"
        :disabled="loadingTags"
      >
      </v-btn>
    </v-card-title>

    <v-card-text class="pa-0 mt-2">
      <v-autocomplete
        v-model="selectedTagIds"
        :items="availableTags"
        item-title="name"
        item-value="id"
        label="Añadir Tags"
        multiple
        chips
        closable-chips
        clearable
        variant="outlined"
        :loading="loadingTags"
        :search="tagSearch"
        @update:search="tagSearch = $event">
        <template v-slot:chip="{ props, item }">
          <v-chip
            v-bind="props"
            :color="item.raw.color"
            variant="flat"
            size="small"
            label
          >
            <span class="text-white text-caption">{{ item.raw.name }}</span>
          </v-chip>
        </template>

        <template v-slot:item="{ props, item }">
          <v-list-item v-bind="props" :title="item.raw.name">
            <template v-slot:prepend>
              <v-icon :color="item.raw.color">mdi-circle</v-icon>
            </template>
          </v-list-item>
        </template>

        <template v-slot:append-item>
          <div v-if="newTagSuggestion && !tagExists(newTagSuggestion)" class="pa-2 d-flex flex-column align-center">
            <v-chip color="primary" class="mb-2">
              Create new Tag: "{{ newTagSuggestion }}"
            </v-chip>
            
            <div class="d-flex flex-wrap justify-center ga-2 mb-2">
              <v-btn
                v-for="color in defaultColors"
                :key="color"
                :color="color"
                size="small"
                icon
                @click="selectedNewTagColor = color"
                :variant="selectedNewTagColor === color ? 'tonal' : 'flat'"
              >
                <v-icon v-if="selectedNewTagColor === color" size="x-small">mdi-check</v-icon>
              </v-btn>
            </div>

            <v-color-picker
              v-model="selectedNewTagColor"
              hide-inputs
              hide-canvas
              hide-sliders
              class="mb-2"
              show-swatches
              :swatches="[defaultColors.slice(0,5), defaultColors.slice(5,10)]"
              :max-swatches="10"
              elevation="0"
            ></v-color-picker>

            <v-btn
              color="success"
              variant="flat"
              block
              :disabled="!newTagSuggestion || !selectedNewTagColor"
              @click="createTagFromSuggestion"
              :loading="creatingTag"
            >
              Create and Add "{{ newTagSuggestion }}"
            </v-btn>
          </div>
          <v-list-item v-else-if="tagSearch && !newTagSuggestion && !loadingTags">
            <v-list-item-title>There are no matching tags.</v-list-item-title>
          </v-list-item>
        </template>
      </v-autocomplete>
      <v-alert v-if="error" type="error" class="mt-2">{{ error }}</v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import { useTaskStore } from '@/stores/task'; // O tu store de Proyectos
import type { Tag } from '@/types/project'; // Asume que Tag tiene { id: number; name: string; color: string; }

const props = defineProps<{
  projectId: number;
  initialTagIds: number[]; // IDs de tags actualmente seleccionadas
}>();

const emit = defineEmits(['update:tags']); // Emite un array de IDs cuando las tags cambian

const taskStore = useTaskStore();
const loadingTags = ref(false);
const creatingTag = ref(false);
const error = ref('');

// --- Estado local para el v-autocomplete ---
const availableTags = ref<Tag[]>([]); // Todas las tags disponibles para este proyecto
const selectedTagIds = ref<number[]>([]); // IDs de las tags seleccionadas en el autocomplete
const tagSearch = ref(''); // Valor del campo de búsqueda/entrada

// --- Estado para la creación de nuevas tags ---
const selectedNewTagColor = ref('#1976D2'); // Color por defecto (primary de Vuetify)
const defaultColors = [ // Paleta de colores predefinidos
  '#1976D2', '#4CAF50', '#FFC107', '#FF5252', '#9C27B0', 
  '#00BCD4', '#FF9800', '#795548', '#607D8B', '#E91E63'
];

// --- Propiedades computadas ---

// Calcula la sugerencia de nueva tag solo si no es un tag existente
const newTagSuggestion = computed(() => {
  const searchTerm = tagSearch.value.trim();
  if (searchTerm && !tagExists(searchTerm)) {
    return searchTerm;
  }
  return null;
});

// Comprueba si una tag ya existe en la lista de disponibles por nombre (insensible a mayúsculas)
const tagExists = (name: string) => {
  return availableTags.value.some(tag => tag.name.toLowerCase() === name.toLowerCase());
};

// --- Watchers ---

// Sincroniza las tags iniciales con el v-autocomplete
watch(() => props.initialTagIds, (newIds) => {
  if (JSON.stringify(selectedTagIds.value) !== JSON.stringify(newIds)) {
    selectedTagIds.value = [...newIds];
  }
}, { immediate: true });

// Emite los cambios de tags cuando selectedTagIds cambia
watch(selectedTagIds, (newIds) => {
  emit('update:tags', newIds);
});

// Resetea el color de la nueva tag cuando la búsqueda cambia
watch(tagSearch, () => {
  selectedNewTagColor.value = defaultColors[0]; // Reset al primer color por defecto
});

// --- Métodos de Carga y Creación ---

// Carga las tags asociadas al proyecto
const fetchProjectTags = async () => {
  loadingTags.value = true;
  error.value = '';
  try {
    // Asumimos que taskStore.fetchProjectTags actualiza taskStore.projectTags
    await taskStore.fetchProjectTags(props.projectId);
    availableTags.value = taskStore.projectTags; // Asume que projectTags es List<Tag>
  } catch (e) {
    error.value = 'Error al cargar las tags del proyecto.';
    console.error(e);
  } finally {
    loadingTags.value = false;
  }
};

// Crea una nueva tag desde la sugerencia y la añade a las seleccionadas
const createTagFromSuggestion = async () => {
  if (!newTagSuggestion.value || !selectedNewTagColor.value) return;

  creatingTag.value = true;
  error.value = '';
  try {
    const newTag = await taskStore.createProjectTag(
      props.projectId,
      newTagSuggestion.value,
      selectedNewTagColor.value
    );
    
    // Si la creación fue exitosa:
    // 1. Añade la nueva tag a las disponibles
    availableTags.value.push(newTag);
    // 2. Selecciona la nueva tag
    selectedTagIds.value = [...selectedTagIds.value, newTag.id];
    // 3. Limpia el campo de búsqueda
    tagSearch.value = '';
    // 4. Reinicia el color seleccionado
    selectedNewTagColor.value = defaultColors[0];

  } catch (e) {
    error.value = `Error al crear la tag "${newTagSuggestion.value}".`;
    console.error(e);
  } finally {
    creatingTag.value = false;
  }
};

// Maneja la pulsación de la tecla Enter en el campo de búsqueda
const handleEnterKey = (event: KeyboardEvent) => {
  if (newTagSuggestion.value && !tagExists(newTagSuggestion.value)) {
    event.preventDefault(); // Previene que el formulario se envíe si hay uno
    createTagFromSuggestion();
  }
};

// --- Lifecycle Hook ---
onMounted(() => {
  fetchProjectTags();
});
</script>

<style scoped>
/* Estilos para el título consistente con el resto de la aplicación */
.primary-title {
  background-color: var(--v-theme-primary);
  color: white;
  padding: 16px 24px;
}
</style>