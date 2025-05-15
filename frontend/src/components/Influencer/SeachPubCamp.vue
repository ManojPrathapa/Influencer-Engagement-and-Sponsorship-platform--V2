<script setup>
import Logout from "@/views/Logout/performLogout.vue";
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

// Reactive state
const campaigns = ref([]);
const searchQuery = ref("");
const sortKey = ref("");

// Fetch campaigns
const fetchCampaigns = async () => {
  try {
    const response = await axios.get("http://127.0.0.1:5000/api/available-campaigns");
    campaigns.value = response.data;
  } catch (error) {
    console.error("Error fetching campaigns:", error);
  }
};

// Format date
const formatDate = (dateString) => {
  const options = { year: "numeric", month: "short", day: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

// Send Ad Request
const token = ref(localStorage.getItem("token"));

const sendAdRequest = async (campaignId) => {
  const decodedToken = jwtDecode(token.value);

  try {
    console.log(`Sending Ad request for campaign ID: ${campaignId}`);

    const response = await axios.post(
      `http://127.0.0.1:5000/influencer/sendAdReqst/${campaignId}`, 
      {}, 
      {
        headers: {
          Authorization: `Bearer ${token.value}`, // Ensure token is being set
        },
      }
    );

    if (response.data.success) {
      alert("Ad request sent successfully!");
    } else {
      alert("Failed to send ad request: " + response.data.message);
    }
  } catch (error) {
    console.error("Error sending ad request:", error);
    alert("An error occurred while sending the ad request.");
  }
};

// Filter and sort campaigns
const filteredAndSortedCampaigns = computed(() => {
  let filtered = campaigns.value.filter((campaign) => {
    const query = searchQuery.value.toLowerCase();
    return (
      campaign.name.toLowerCase().includes(query) ||
      campaign.niche.toLowerCase().includes(query)
    );
  });

  if (sortKey.value.includes("name")) {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortKey.value.includes("budget")) {
    filtered.sort((a, b) => parseFloat(a.budget) - parseFloat(b.budget));
  }

  if (sortKey.value.endsWith("desc")) {
    filtered.reverse();
  }

  return filtered;
});

// Lifecycle hook
onMounted(() => {
  fetchCampaigns();
});
</script>

<template>
  <Logout DashboardTitle="Search Public Campaigns"></Logout>
  <div class="container mt-5">
    <h2 class="text-center mb-4">Campaigns List</h2>

    <!-- Search Bar -->
    <div class="form-group">
      <input
        v-model="searchQuery"
        type="text"
        class="form-control"
        placeholder="Search by name or niche"
      />
    </div>

    <!-- Sorting Options -->
    <div class="form-group">
      <select v-model="sortKey" class="form-control">
        <option disabled value="">Sort by</option>
        <option value="name-asc">Name (A-Z)</option>
        <option value="name-desc">Name (Z-A)</option>
        <option value="budget-asc">Budget (Ascending)</option>
        <option value="budget-desc">Budget (Descending)</option>
      </select>
    </div>

    <!-- Campaigns Table -->
    <table class="table table-hover mt-3">
      <thead class="thead-dark">
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th>Budget</th>
          <th>Goals</th>
          <th>Niche</th>
          <th>Send Ad Request</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="campaign in filteredAndSortedCampaigns"
          :key="campaign.campaign_id"
          class="table-row"
        >
          <td>{{ campaign.name }}</td>
          <td>{{ campaign.description }}</td>
          <td>{{ formatDate(campaign.start_date) }}</td>
          <td>{{ formatDate(campaign.end_date) }}</td>
          <td>${{ parseFloat(campaign.budget).toFixed(2) }}</td>
          <td>{{ campaign.goals }}</td>
          <td>{{ campaign.niche }}</td>
          <td>
            <button
              class="btn btn-primary"
              @click="sendAdRequest(campaign.campaign_id)"
            >
              Send Ad Request
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: auto;
}

.table-hover tbody tr:hover {
  background-color: #0fb3b1; /* Light hover effect */
}

.table-row:hover {
  background-color: #7e1414; /* Similar hover effect for rows */
}

.thead-dark th {
  background-color: #27619b;
  color: white;
}

.form-group {
  margin-bottom: 1.5rem;
}

.text-center {
  text-align: center;
}

.btn-primary {
  background-color: #15e364;
  border-color: #0ee034;
}

.btn-primary:hover {
  background-color: #b21de4;
  border-color: #0996c5;
}
</style>
