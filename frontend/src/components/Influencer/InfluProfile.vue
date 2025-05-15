<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import performLogout from '@/views/Logout/performLogout.vue';

// Reactive state for profile data
const profileData = ref({
  name: '',
  niche: '',
  reach: 0,
  category : '',
});

// Fetch profile data
const fetchProfileData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/influencer/profile', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    profileData.value = response.data.influ_data;
  } catch (error) {
    console.error('Error fetching profile data:', error);
  }
};

// Update profile data
const updateProfile = async () => {
  try {
    await axios.post('http://localhost:5000/influencer/profile', profileData.value, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    alert('Profile updated successfully!');
  } catch (error) {
    console.error('Error updating profile:', error);
    alert('An error occurred while updating the profile.');
  }
};

// Lifecycle hook to fetch profile data when component is mounted
onMounted(() => {
  fetchProfileData();
});
</script>

<template>
    <performLogout DashboardTitle="Profile" />
  <div class="container mt-5">
    

    <h2 class="text-center mb-4">Edit Profile</h2>

    <form @submit.prevent="updateProfile">
      <!-- Name -->
      <div class="form-group">
        <label for="name">Name</label>
        <input
          id="name"
          v-model="profileData.name"
          type="text"
          class="form-control"
          placeholder="Enter your name"
          required
        />
      </div>

      <!-- Niche -->
      <div class="form-group">
        <label for="niche">Niche</label>
        <input
          id="niche"
          v-model="profileData.niche"
          type="text"
          class="form-control"
          placeholder="Enter your niche"
          required
        />
      </div>

        <!-- Category -->
        <div class="form-group">
    <label for="category">Category</label>
    <input
        id="category"
        v-model="profileData.category"
        type="text"
        class="form-control"
        placeholder="Enter your category"
        required
    />
    </div>

      <!-- Reach -->
      <div class="form-group">
        <label for="reach">Reach</label>
        <input
          id="reach"
          v-model.number="profileData.reach"
          type="number"
          min="0"
          class="form-control"
          placeholder="Enter your reach"
          required
        />
      </div>

      <!-- Submit Button -->
      <button type="submit" class="btn btn-primary">Update Profile</button>
    </form>
  </div>
</template>

<style scoped>
.container {
  max-width: 600px;
  margin: auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.btn-primary {
  margin-top: 1rem;
}
</style>
