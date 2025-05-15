<template>
    <div class="register container mt-5">
      <h1 class="text-center mb-4">New Sponsor Registration</h1>
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
            <option value="sponsor">Sponsor</option>
          </select>
        </div>
        <div class="form-group mb-3">
          <label for="company_name">Company Name:</label>
          <input v-model="company_name" type="text" id="company_name" class="form-control" required />
        </div>
        <div class="form-group mb-3">
          <label for="industry">Industry:</label>
          <input v-model="industry" type="text" id="industry" class="form-control" required />
        </div>
        <div class="form-group mb-3">
          <label for="budget">Budget:</label>
          <input v-model="budget" type="number" min="0" id="budget" class="form-control" required />
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
      role: 'sponsor', // Set role to 'sponsor' directly
      company_name : '',
      industry : '',
      budget :'',

      errorMessage: '',
      successMessage: '', // Add success message property
    };
  },
  computed: {
    isFormValid() {
      return this.username && this.password && this.email && this.company_name && this.industry && this.budget;
    },
  },
  methods: {
    async register() {
      try {
        await axios.post('/sponsor/register', {
          username: this.username,
          email: this.email,
          password: this.password,
          role: this.role,
          company_name : this.company_name,
          industry : this.industry,
          budget : this.budget,

        });
        this.successMessage = 'Registration successful!! \n Redirecting to Login page (wait)'; // Set success message
        this.errorMessage = ''; // Clear any previous error message
        
        setTimeout(() => {
          this.$router.push('/sponsor/login');
        }, 2000);
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
  