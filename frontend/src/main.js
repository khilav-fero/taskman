// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// Ag-Grid Module Registration
import { ModuleRegistry } from '@ag-grid-community/core';
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
ModuleRegistry.registerModules([ClientSideRowModelModule]);

// Import custom components
import ActionCellRenderer from '@/components/ActionCellRenderer.vue';


const vuetify = createVuetify({
  components,
  directives,
  icons: { defaultSet: 'mdi' },
})

const app = createApp(App)
const pinia = createPinia()

// Register components globally
app.component('actionCellRenderer', ActionCellRenderer);

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')