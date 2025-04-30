import { createApp } from 'vue'
import App from './App.vue' 
import { createPinia } from 'pinia' 
import router from './router' 

// --- Vuetify ---
import 'vuetify/styles' 
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives' 
import '@mdi/font/css/materialdesignicons.css' 

// Create Vuetify instance
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi', 
  },
})
// --- End Vuetify ---

// Create the main Vue app instance
const app = createApp(App)

// Create Pinia instance for state management
const pinia = createPinia()

// Use the plugins
app.use(vuetify) // Use Vuetify components/styles
app.use(pinia)   // Use Pinia for state management
app.use(router)  // Use Vue Router for navigation

app.mount('#app')