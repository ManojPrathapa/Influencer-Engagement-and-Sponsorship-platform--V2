import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; 
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import axios from 'axios';
import store from './store';
import { jwtDecode } from "jwt-decode";





axios.defaults.baseURL = 'http://localhost:5000';

createApp(App)
  .use(router)
  .use(store)
  .mount('#app');
