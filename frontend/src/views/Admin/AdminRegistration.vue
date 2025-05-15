<template>
  <div class="register container mt-5">
    <h1 class="text-center mb-4">Admin Registration</h1>
    <form @submit.prevent="register" class="needs-validation" novalidate>
      <div class="form-group mb-3">
        <label for="username">Username:</label>
        <input v-model="username" type="text" id="username" class="form-control" required />
      </div>
      <div class="form-group mb-3">
        <label for="email">Email:</label>
        <input v-model="email" type="email" id="email" class="form-control" required />
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
      <div class="form-group mb-3">
        <label for="role">Role:</label>
        <select v-model="role" id="role" class="form-control" required>
          <option value="admin">Admin</option>
        </select>
      </div>
      <button :disabled="!isFormValid" type="submit" class="btn btn-primary btn-block">Register</button>
      <p v-if="errorMessage" class="alert alert-danger mt-3">{{ errorMessage }}</p>
      <p v-if="successMessage" class="alert alert-success mt-3">{{ successMessage }}</p>
    </form>
  </div>
</template>





<script>
import axios from 'axios';

export default {
data() {
  return {
    username: '',
    email: '',
    password: '',
    role: 'admin', // Set role to 'admin' directly
    errorMessage: '',
    successMessage: '', // Add success message property
  };
},
computed: {
  isFormValid() {
    return this.username && this.password && this.email;
  },
},
methods: {
  async register() {
    try {
      await axios.post('/admin/register', {
        username: this.username,
        email: this.email,
        password: this.password,
        role: this.role,
      });
      this.successMessage = 'Registration successful !\nRedirecting to Login page (wait)'; // Set success message
      this.errorMessage = ''; // Clear any previous error message
      
      setTimeout(() => {
        this.$router.push('/admin/login');
      }, 3000);
    } catch (error) {
      this.errorMessage = error.response.data.message || 'Registration failed';
      this.successMessage = ''; // Clear any previous success message
    }
  },
},
};
</script>


<style scoped>
/* Add your styles here */
</style>
