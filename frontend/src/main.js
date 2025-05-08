import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import '@mdi/font/css/materialdesignicons.css'

import { ModuleRegistry } from '@ag-grid-community/core';
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
ModuleRegistry.registerModules([ClientSideRowModelModule]);

import ActionCellRenderer from '@/components/ActionCellRenderer.vue';

const modernDarkTheme = {
  dark: true,
  colors: {
    background: '#1F2937',
    surface: '#2B3648',
    primary: '#3B82F6',
    'primary-darken-1': '#2563EB',
    secondary: '#6B7280',
    'secondary-darken-1': '#4B5563',
    accent: '#10B981',
    error: '#EF4444',
    info: '#3B82F6',
    success: '#10B981',
    warning: '#F59E0B',

    'on-background': '#F3F4F6',
    'on-surface': '#E5E7EB',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-accent': '#FFFFFF',
    'on-error': '#FFFFFF',
    'on-success': '#FFFFFF',
    'on-warning': '#0F172A',
  },
};

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'modernDarkTheme',
    themes: {
      modernDarkTheme,
    },
  },
})

const app = createApp(App)
const pinia = createPinia()

app.component('actionCellRenderer', ActionCellRenderer);

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')