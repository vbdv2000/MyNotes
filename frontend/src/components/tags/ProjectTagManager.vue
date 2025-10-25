<template>
    <div>
        <v-select
            v-model="selectedTagIds"
            :items="availableTags"
            item-title="name"
            item-value="id"
            label="Tags"
            multiple
            chips
            clearable
            placeholder="Selecciona o crea una nueva Tag"
            :loading="loading"
            variant="outlined"
            class="mb-3"
            @update:modelValue="$emit('update:tags', selectedTagIds)"
        >
            <template v-slot:prepend-item>
                <v-list-item class="mb-2">
                    <v-text-field
                        v-model="newTagName"
                        label="Crear nueva Tag..."
                        append-inner-icon="mdi-plus"
                        density="compact"
                        hide-details
                        @click:append-inner="createTagAndSelect"
                        @keyup.enter="createTagAndSelect"
                    >
                        <template v-slot:append-inner>
                           <v-btn icon="mdi-plus" variant="text" size="small" @click="createTagAndSelect" :disabled="!newTagName || loading"></v-btn>
                        </template>
                    </v-text-field>
                </v-list-item>
                <v-divider></v-divider>
            </template>

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
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useTaskStore } from '@/stores/task'; 
// Asume que tienes un tipo Tag
interface Tag { id: number; name: string; color: string; }

const props = defineProps<{
    projectId: number;
    initialTagIds: number[];
}>();

const emit = defineEmits(['update:tags']);

const taskStore = useTaskStore();
const loading = ref(false);
const newTagName = ref('');
const availableTags = ref<Tag[]>([]);
const selectedTagIds = ref<number[]>(props.initialTagIds);

// --- Lifecycle y Carga de Datos ---
onMounted(() => {
    fetchProjectTags();
});

const fetchProjectTags = async () => {
    loading.value = true;
    try {
        // 💡 Llama a GET /api/projects/{project_id}/tags
        const tags: Tag[] = await taskStore.fetchProjectTags(props.projectId);
        availableTags.value = tags;
    } catch (e) {
        console.error("Error al cargar las tags del proyecto:", e);
    } finally {
        loading.value = false;
    }
};

// --- Lógica de Creación Rápida ---
const createTagAndSelect = async () => {
    const name = newTagName.value.trim();
    if (!name || loading.value) return;

    loading.value = true;
    try {
        // 💡 Llama a POST /api/projects/{project_id}/tags (Crea y asocia)
        const newTag: Tag = await taskStore.createProjectTag(props.projectId, { 
            name: name, 
            color: '#808080' // Color por defecto
        });

        // 1. Si la tag ya existía, el backend la devuelve. Si no, la creamos.
        // Aseguramos que solo esté una vez en la lista de opciones.
        if (!availableTags.value.find(t => t.id === newTag.id)) {
             availableTags.value.push(newTag);
        }
       
        // 2. Seleccionar la tag recién creada/asociada
        if (!selectedTagIds.value.includes(newTag.id)) {
            selectedTagIds.value.push(newTag.id);
        }

        // 3. Limpiar el campo y notificar al padre
        newTagName.value = '';
        emit('update:tags', selectedTagIds.value);

    } catch (e) {
        console.error("Error al crear la tag rápidamente:", e);
    } finally {
        loading.value = false;
    }
};

// Sincronizar tags externas cuando el padre las inicializa
watch(() => props.initialTagIds, (newIds) => {
    selectedTagIds.value = newIds;
}, { immediate: true });
</script>