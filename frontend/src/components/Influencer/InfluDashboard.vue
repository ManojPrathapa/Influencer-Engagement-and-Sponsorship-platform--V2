<template>
  <performLogout DashboardTitle="Manage AD Request" />
  <div>
    <div v-if="flashMessages.length" class="alert alert-danger">
      <ul>
        <li v-for="message in flashMessages" :key="message">{{ message }}</li>
      </ul>
    </div>

    <div>
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <button class="btn btn-primary" @click="navigateToPublicCampaigns">
          See All Public Campaigns
        </button>
        <div class="container"></div>
        <button class="btn btn-warning" @click="navigateToInfluProfile">
          Update Profile
        </button>
      </nav>
    </div>

    <div class="welcome-message">
      <h2>Welcome, {{ userName || "User-Influencer" }}!</h2>
    </div>

    <table v-if="data.length" class="table table-striped table-bordered">
      <thead>
        <tr>
          <th>Campaign Name</th>
          <th>Description</th>
          <th>Goals</th>
          <th>Niche</th>
          <th>Sponsor Name</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th>Message</th>
          <th>Ad Request Status</th>
          <th>Requirements</th>
          <th>Payment Amount</th>
          <th>Negotiated Amount</th>
          <th>Negotiation Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(item, index) in data"
          :key="item.ad_request_id"
          :style="{ backgroundColor: rowColor(index) }"
          class="table-row"
        >
          <td>{{ item.campaign_name }}</td>
          <td>{{ item.description }}</td>
          <td>{{ item.goals }}</td>
          <td>{{ item.niche }}</td>
          <td>{{ item.sponsor_name }}</td>
          <td>{{ item.start_date }}</td>
          <td>{{ item.end_date }}</td>
          <td>{{ item.messages }}</td>
          <td>{{ item.status }}</td>
          <td>{{ item.requirements }}</td>
          <td>{{ item.payment_amount }}</td>
          <td>{{ item.negotiated_amount }}</td>
          <td>{{ item.negotiation_status }}</td>
          <td>
            <div v-if="item.negotiation_status === 'pending'">
              <button
                class="btn btn-success"
                @click="acceptAdRequest(item.ad_request_id)"
              >
                Accept
              </button>
              <button
                class="btn btn-danger"
                @click="rejectAdRequest(item.ad_request_id)"
              >
                Reject
              </button>
              <button
                class="btn btn-warning"
                @click="negotiateAdRequest(item.ad_request_id)"
              >
                Negotiate
              </button>
            </div>
            <div v-else>
              <h5>
                <span class="badge text-bg-secondary">{{
                  item.negotiation_status
                }}</span>
              </h5>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>No Ad Requests to show!</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { jwtDecode } from "jwt-decode";
import performLogout from "@/views/Logout/performLogout.vue";

const router = useRouter();

const flashMessages = ref([]);
const userName = ref(""); // Update with actual user name if available
const data = ref([]); // List of ad requests

const navigateToPublicCampaigns = () => {
  router.push("/influencer/search_pubcamp");
};

const navigateToInfluProfile = () => {
  router.push("/influencer/profile");
};

const acceptAdRequest = (adRequestId) => {
  window.location.href = `/influencer/acceptAdRequest/${adRequestId}`;
};

const rejectAdRequest = (adRequestId) => {
  window.location.href = `/influencer/rejectAdRequest/${adRequestId}`;
};

const negotiateAdRequest = (adRequestId) => {
  window.location.href = `/influencer/negoAdRequest/${adRequestId}`;
};

const rowColor = (index) => {
  // Define an array of bright colors
  const colors = ["#FFEB3B", "#FF7043", "#81C784", "#FFCDD2", "#F06292", "#64B5F6"];
  return colors[index % colors.length]; // Rotate colors based on index
};

onMounted(async () => {
  try {
    const token = localStorage.getItem("token");
    const decodedToken = jwtDecode(token);
    userName.value = decodedToken.username;
    const response = await axios.get("/influencer/dashboard", {
      headers: { Authorization: `Bearer ${token}` },
    });
    data.value = response.data.data;
  } catch (error) {
    flashMessages.value.push("Error fetching data: " + error.message);
  }
});
</script>

<style scoped>
.welcome-message {
  margin-bottom: 20px;
  margin-left: 20px;
}

.table-hover tbody tr:hover {
  background-color: #3521d2; /* Light hover effect */
}

.table-row:hover {
  background-color: #3524c9; /* Similar hover effect for rows */
}

.btn-success:hover {
  background-color: #28a745;
}

.btn-danger:hover {
  background-color: #dc3545;
}

.btn-warning:hover {
  background-color: #ffc107;
}

.badge {
  font-size: 0.9rem;
}
</style>
