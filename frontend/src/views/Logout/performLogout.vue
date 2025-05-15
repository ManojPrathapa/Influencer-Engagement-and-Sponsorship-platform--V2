<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <a class="navbar-brand">{{ DashboardTitle }}</a>
      <ul class="navbar-nav ml-auto">
        <li class="nav-item">
          <button class="btn btn-outline-light" @click="performLogout">Logout</button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import axios from 'axios';

export default {
  props: {
    DashboardTitle: {
      type: String,
      required: true
    }
  },
  methods: {
    ...mapActions(['logout', 'setError', 'clearMessages']),
    
    async performLogout() {
      try {
        // Trigger the backend logout API
        await axios.post('http://localhost:5000/signout');

        // Call Vuex logout action
        await this.logout();
        
        // Clear any previous messages
        this.clearMessages();
        
        // Redirect to the home page
        this.$router.push('/').then(() => {
          // Optionally clear messages on redirect
          this.clearMessages();
        });
      } catch (error) {
        console.error("Logout failed:", error);
        this.setError("Logout failed. Please try again.");
      }
    }
  }
};
</script>
