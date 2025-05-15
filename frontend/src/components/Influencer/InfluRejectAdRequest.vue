<template>
    <div class="container">
      <h2 class="my-4">Ad Request Details</h2>
      
      <!-- Flash messages -->
      <div v-if="flashMessages.length" class="alert alert-success">
        <ul>
          <li v-for="message in flashMessages" :key="message">{{ message }}</li>
        </ul>
      </div>
  
      <!-- Ad request details -->
      <div v-if="adRequest">
        <dl class="row">
          <dt class="col-sm-3">Campaign Name:</dt>
          <dd class="col-sm-9">{{ adRequest.campaign_name }}</dd>
  
          <dt class="col-sm-3">Description:</dt>
          <dd class="col-sm-9">{{ adRequest.description }}</dd>
  
          <dt class="col-sm-3">Start Date:</dt>
          <dd class="col-sm-9">{{ formatDate(adRequest.start_date) }}</dd>
  
          <dt class="col-sm-3">End Date:</dt>
          <dd class="col-sm-9">{{ formatDate(adRequest.end_date) }}</dd>
  
          <dt class="col-sm-3">Goals:</dt>
          <dd class="col-sm-9">{{ adRequest.goals }}</dd>
  
          <dt class="col-sm-3">Niche:</dt>
          <dd class="col-sm-9">{{ adRequest.niche }}</dd>
  
          <dt class="col-sm-3">Sponsor Name:</dt>
          <dd class="col-sm-9">{{ adRequest.sponsor_name }}</dd>
  
          <dt class="col-sm-3">Messages:</dt>
          <dd class="col-sm-9">{{ adRequest.messages }}</dd>
  
          <dt class="col-sm-3">Payment Amount:</dt>
          <dd class="col-sm-9">${{ adRequest.payment_amount }}</dd>
  
          <dt class="col-sm-3">Negotiated Amount:</dt>
          <dd class="col-sm-9">${{ adRequest.negotiated_amount }}</dd>
  
          <dt class="col-sm-3">Requirements:</dt>
          <dd class="col-sm-9">{{ adRequest.requirements }}</dd>
  
          <dt class="col-sm-3">Status:</dt>
          <dd class="col-sm-9">{{ adRequest.status }}</dd>
  
          <dt class="col-sm-3">Negotiation Status:</dt>
          <dd class="col-sm-9">{{ adRequest.negotiation_status }}</dd>
        </dl>
  
        <button type="button" class="btn btn-danger" @click="rejectAdRequest">Reject</button>
      </div>
      <div v-else>
        <p>Loading ad request details...</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import { useRoute, useRouter } from 'vue-router';
  
  const adRequest = ref(null);
  const flashMessages = ref([]);
  const route = useRoute();
  const router = useRouter();
  const adRequestId = route.params.ad_request_id; // Access route parameter
  
  const fetchAdRequestDetails = async () => {
    try {
      const token = localStorage.getItem("token");
      
      const response = await axios.get(`http://localhost:5000/influencer/rejectAdRequest/${adRequestId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      adRequest.value = response.data;
    } catch (error) {
      console.error('Error fetching ad request details:', error);
    }
  };
  
  const rejectAdRequest = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(`http://localhost:5000/influencer/rejectAdRequest/${adRequestId}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      flashMessages.value = [response.data.message];
      
      // Redirect after 3 seconds
      setTimeout(() => {
        router.push('/influencer/dashboard');
      }, 3000);
    } catch (error) {
      console.error('Error Rejecting ad request:', error);
      flashMessages.value = ['Error Rejecting ad request. Please try again.'];
    }
  };
  
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  onMounted(() => {
    fetchAdRequestDetails();
  });
  </script>
  
  <style scoped>
  .container {
    margin: 20px;
  }
  
  .row {
    margin-bottom: 10px;
  }
  
  .col-sm-3 {
    font-weight: bold;
  }
  
  .col-sm-9 {
    margin-bottom: 10px;
  }
  </style>
  