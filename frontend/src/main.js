// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import router from './router'; // Make sure './router' correctly points to your router setup

// Vuetify
import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css'; // Material Design Icons CSS

// --- Ag-Grid Module Registration ---
// ❌ REMOVED global registration from here. Modules will be passed via props.
// import { ModuleRegistry } from '@ag-grid-community/core';
// import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
// ModuleRegistry.registerModules([ClientSideRowModelModule]);
// --- End Ag-Grid Module Registration Removal ---

// --- Initialize Plugins ---
const pinia = createPinia();

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi', // Set Material Design Icons as the default icon set
  },
  // Add any other Vuetify configurations here
});

// --- Create and Configure Vue App ---
const app = createApp(App);

app.use(pinia);   // Use Pinia for state management
app.use(router);  // Use Vue Router for navigation
app.use(vuetify); // Use Vuetify for UI components

// --- Mount the App ---
app.mount('#app');