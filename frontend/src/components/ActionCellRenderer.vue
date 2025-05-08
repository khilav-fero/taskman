<template>
    <div class="d-flex align-center justify-center fill-height">
      <v-tooltip text="Edit Task" location="top">
          <template v-slot:activator="{ props: tooltip }">
              <v-btn
                  v-if="canManage"
                  v-bind="tooltip"
                  icon="mdi-pencil"
                  size="x-small"
                  variant="tonal"
                  color="primary"
                  class="mr-1"
                  @click="editTask"
                  :aria-label="'Edit task ' + params.data.title"
              />
           </template>
      </v-tooltip>
  
       <v-tooltip text="Delete Task" location="top">
          <template v-slot:activator="{ props: tooltip }">
              <v-btn
                  v-if="canManage"
                  v-bind="tooltip"
                  icon="mdi-delete"
                  size="x-small"
                  variant="tonal"
                  color="error"
                  @click="deleteTask"
                   :aria-label="'Delete task ' + params.data.title"
              />
           </template>
      </v-tooltip>
      <!-- Add View Details button here if needed -->
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  
  // Props passed automatically by Ag-Grid
  const props = defineProps({
      params: {
          type: Object,
          required: true
      }
  });
  
  const canManage = computed(() => props.params.canManage?.value ?? false);
  
  const editTask = () => {
      if (props.params.onEditClick) {
          props.params.onEditClick(props.params.data); // Pass full row data
      } else {
          console.error("onEditClick handler not provided in cellRendererParams");
      }
  };
  
  const deleteTask = () => {
      if (props.params.onDeleteClick) {
          props.params.onDeleteClick(props.params.data.id); // Pass only the ID
      } else {
           console.error("onDeleteClick handler not provided in cellRendererParams");
      }
  };
  
  </script>
  
  <style scoped>
  div {

  }
  </style>