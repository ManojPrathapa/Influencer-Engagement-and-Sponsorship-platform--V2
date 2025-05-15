<script setup>
import Logout from "@/views/Logout/performLogout.vue";
import axios from "axios";
import { jwtDecode } from "jwt-decode";
</script>

<template>
  <div>
    <Logout DashboardTitle="Sponsor Manage Campaign"></Logout>

    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="ml-auto">
        <button
          class="btn btn-secondary"
          @click="navigateTo('search_influencer')"
        >
          Search Influencers
        </button>
        <button class="btn btn-primary" @click="exportToCSV">
          Export as CSV
        </button>
      </div>
    </nav>
    <p v-if="errorMessage" class="alert alert-danger mt-3">
      {{ errorMessage }}
    </p>
    <div class="container">
      <h1>Welcome, {{ userName }}</h1>
      <p>Manage your campaigns below:</p>

      <div id="flash" v-if="messages.length">
        <div class="alert alert-danger">
          <ul>
            <li v-for="message in messages" :key="message">{{ message }}</li>
          </ul>
        </div>
      </div>

      <button class="btn btn-success mb-3" @click="navigateTo('addcampaign')">
        + Add New Campaign
      </button>

      <div v-if="campaignData.length" class="row">
        <table class="table table-striped table-bordered campaign-list">
          <thead class="thead-dark">
            <tr>
              <th>Campaign Name</th>
              <th>Description</th>
              <th>Niche</th>
              <th>Budget</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Goals</th>
              <th>Visibility</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="data in campaignData" :key="data.campaign_id">
              <td>{{ data.name }}</td>
              <td>{{ data.description }}</td>
              <td>{{ data.niche }}</td>
              <td>{{ data.budget }}</td>
              <td>{{ formatDate(data.start_date) }}</td>
              <td>{{ formatDate(data.end_date) }}</td>
              <td>{{ data.goals }}</td>
              <td>{{ data.visibility }}</td>
              <td class="action-buttons">
                <button
                  class="btn btn-warning btn-sm"
                  @click="editCampaign(data.campaign_id)"
                >
                  Edit
                </button>
                <button
                  class="btn btn-danger btn-sm"
                  @click="deleteCampaign(data.campaign_id)"
                >
                  Delete
                </button>
                <button
                  class="btn btn-primary btn-sm"
                  @click="AdRequest(data.campaign_id)"
                >
                  AdRequest
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else>
        <h3 style="color: red; font-weight: bold">No Campaigns to show!!</h3>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userName: "", // This will be populated with the username from the token
      messages: [], // Replace with actual flash messages
      campaignData: [], // Will be populated with actual campaign data
      errorMessage: "",
    };
  },
  async created() {
    try {
      // Decode the token to get the username
      const token = this.$store.state.token;
      const decodedToken = jwtDecode(token);
      this.userName = decodedToken.username; // Extract and set the username

      const response = await axios.get(
        "http://localhost:5000/sponsor/dashboard/data",
        {
          headers: { Authorization: `Bearer ${this.$store.state.token}` },
        }
      );
      if (response.data.campaigns) {
        this.campaignData = response.data.campaigns;
      } else {
        this.errorMessage = `Unexpected response structure: ${response.data}`;
        console.error("Unexpected response structure:", response.data);
      }
    } catch (error) {
      this.errorMessage = error;
      console.error("Failed to fetch dashboard data:", error);
    }
  },
  methods: {
    navigateTo(route) {
      window.location.href = `/sponsor/${route}`;
    },
    editCampaign(campaignId) {
      window.location.href = `/sponsor/editcampaign/${campaignId}`;
    },
    async deleteCampaign(campaignId) {
      const confirmDelete = window.confirm(
        "Do you really want to delete this campaign?"
      );
      if (confirmDelete) {
        try {
          const response = await axios.delete(
            `http://localhost:5000/sponsor/deletecampaign/${campaignId}`,
            {
              headers: { Authorization: `Bearer ${this.$store.state.token}` },
            }
          );
          if (response.data.success) {
            this.campaignData = this.campaignData.filter(
              (c) => c.campaign_id !== campaignId
            );
            alert("Campaign deleted successfully.");
          } else {
            this.errorMessage = response.data.message;
          }
        } catch (error) {
          this.errorMessage =
            "An error occurred while trying to delete the campaign.";
          console.error("Delete campaign error:", error);
        }
      }
    },
    AdRequest(campaignId) {
      window.location.href = `/sponsor/adrequest/${campaignId}`;
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "2-digit",
        day: "2-digit",
        year: "numeric",
      });
    },
    exportToCSV() {
      const token = this.$store.state.token;
      axios
        .get("http://localhost:5000/sponsor/export_campaigns", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: "blob", // Important for downloading files
        })
        .then((response) => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "campaigns.csv");
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link); // Clean up
        })
        .catch((error) => {
          this.errorMessage = "Error exporting campaigns. Please try again.";
          console.error("Error exporting campaigns:", error);
        });
    },
  },
};
</script>

<style scoped>
/* Style for table rows with alternating background colors */
.campaign-list tbody tr:nth-child(even) {
  background-color: #10b339; /* Light gray color for even rows */
}

.campaign-list tbody tr:nth-child(odd) {
  background-color: #d4292f; /* White color for odd rows */
}

/* Hover effect for table rows */
.campaign-list tbody tr:hover {
  background-color: #f02dbf; /* Light gray on hover */
}

/* Style for the action buttons */
.action-buttons button:hover {
  opacity: 0.8; /* Slightly transparent on hover */
}

/* Hover effect for action buttons */
.action-buttons button.btn-warning:hover {
  background-color: #e0a800; /* Darker yellow for Edit button */
}

.action-buttons button.btn-danger:hover {
  background-color: #d9534f; /* Darker red for Delete button */
}

.action-buttons button.btn-primary:hover {
  background-color: #007bff; /* Darker blue for AdRequest button */
}
</style>
