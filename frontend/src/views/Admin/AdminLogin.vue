<template>
  <div class="login container mt-5">
    <h1 class="text-center mb-4">Admin Login</h1>
    <form @submit.prevent="login" class="needs-validation" novalidate>
      <div class="form-group mb-3">
        <label for="username">Username:</label>
        <input v-model="username" type="text" id="username" class="form-control" required />
      </div>
      <div class="form-group mb-3">
        <label for="password">Password:</label>
        <div class="input-group">
          <input :type="showPassword ? 'text' : 'password'" v-model="password" id="password" class="form-control" required />
          <div class="input-group-append">
            <span class="input-group-text">
              <input type="checkbox" id="show-password" v-model="showPassword" />
              <label for="show-password" class="mb-0 ml-2">Show</label>
            </span>
          </div>
        </div>
      </div>
      <button :disabled="!isFormValid" type="submit" class="btn btn-primary btn-block">Login</button>
      
      <p v-if="errorMessage" class="text-danger mt-3">{{ errorMessage }}</p>
    </form>
    <button @click="$router.push('/admin/register')" class="btn btn-secondary btn-block mt-3">New Admin Registration</button>
  </div>
</template>

<script>
import axios from 'axios';
import { mapActions } from 'vuex'; // Import mapActions to map Vuex actions

export default {
  data() {
    return {
      username: '',
      password: '',
      showPassword: false, // Initialize showPassword
      errorMessage: '',
    };
  },
  computed: {
    isFormValid() {
      return this.username && this.password;
    },
  },
  methods: {
    ...mapActions(['login']), // Map Vuex login action

    async login() {
      try {
        const response = await axios.post('/admin/login', {
          username: this.username,
          password: this.password,
        });

        // console.log('Server Response:', response.data);
        // Extract token and role from the response
        const { token, role } = response.data;

        // Update Vuex store with token and role
        this.$store.dispatch('login', { token, role });

        // Redirect to the dashboard
        this.$router.push('/admin/dashboard');
      } catch (error) {
        console.error('Login error:', error); // Log error for debugging
        this.errorMessage = error.response?.data?.message || 'Login failed';
      }
    },
  },
};
</script>
