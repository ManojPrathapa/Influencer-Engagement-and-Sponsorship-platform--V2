<template>
  <div>
    <!-- Title -->
    <div id="title">
      <h1>Influencia</h1>
    </div>

    <!-- Flash Messages -->
    <div id="flash" v-if="messages && messages.length > 0">
      <div class="alert alert-danger">
        <ul>
          <li v-for="message in messages" :key="message">{{ message }}</li>
        </ul>
      </div>
    </div>

    <!-- Error and Success Messages -->
    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <!-- Body Content -->
    <div class="body-content">
      <div id="button_body">
        <h2>Welcome to</h2>
        <h3 class="platform-heading">Influencer Engagement and Sponsorship Platform - V2</h3>
        <div class="button">
          <button
            class="btn btn-role"
            @click="goTo('/sponsor/login')"
          >
            Sponsor
          </button>
          <button
            class="btn btn-role"
            @click="goTo('/influencer/login')"
          >
            Influencer
          </button>
        </div>
      </div>
    </div>

    <!-- Admin Login -->
    <div id="admin-login">
      <a href="/admin/login">
        <button class="btn btn-admin">Admin Login Only</button>
      </a>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: "Index",
  computed: {
    ...mapGetters(['errorMessage', 'successMessage']),
    messages() {
      return [this.errorMessage, this.successMessage].filter(Boolean);
    }
  },
  methods: {
    goTo(path) {
      this.$router.push(path);
    },
  }
};
</script>

<style scoped>
/* General Styling */
body {
  margin: 0;
  font-family: "Arial", sans-serif;
  background-color: #e6d9f5; /* Light purple background */
}

/* Title */
#title {
  text-align: center;
  margin: 20px 0;
  color: #4b0082; /* Indigo */
  font-size: 3rem;
}

/* Flash Messages */
#flash {
  width: 100%;
  padding: 10px;
  text-align: center;
}

/* Error and Success Alerts */
.alert-danger, .alert-success {
  padding: 10px;
  border-radius: 5px;
  text-align: center;
  margin: 10px auto;
  max-width: 600px;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.alert-success {
  color: #155724;
  background-color: #d4edda;
  border-color: #c3e6cb;
}

/* Body Content */
.body-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 70vh;
}

/* Button Body */
#button_body {
  text-align: center;
}

#button_body h2 {
  margin-bottom: 10px; /* Adjusted spacing */
}

#button_body .platform-heading {
  margin-bottom: 30px;
  color: #4b0082; /* Indigo color matching the 'Influencia' title */
}

/* Role Buttons */
.button {
  display: flex;
  justify-content: center; /* Centers buttons horizontally */
  gap: 20px;
}

.btn-role {
  background-color: #90ee90; /* Light green */
  color: white;
  border: none;
  height: 150px;
  width: 200px;
  padding: 15px 30px;
  cursor: pointer;
  border-radius: 5px;
  font-size: 20px;
  font-weight: 500;
  transition: all 0.3s ease-in-out;
}

.btn-role:hover {
  background-color: #32cd32; /* Lime green on hover */
  color: white;
}

/* Admin Login Button */
#admin-login {
  text-align: center;
  margin-top: 20px;
}

.btn-admin {
  background-color: #4b0082; /* Indigo */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.btn-admin:hover {
  background-color: #9370db; /* Medium purple on hover */
  color: white;
}
</style>
