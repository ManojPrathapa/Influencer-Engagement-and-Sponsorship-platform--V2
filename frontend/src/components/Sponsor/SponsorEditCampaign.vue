<script setup>
import Logout from "@/views/Logout/performLogout.vue";
import axios from "axios";
</script>

<template>
  <div>
    <Logout DashboardTitle="Sponsor Manage Campaign"></Logout>
  </div>
  <p v-if="successMessage" class="alert alert-success mt-3">
    {{ successMessage }}
  </p>
  <div>
    <div class="container">
      <div v-if="messages.length" class="alert alert-danger">
        <ul>
          <li v-for="message in messages" :key="message">{{ message }}</li>
        </ul>
      </div>

      <h2>Update the Campaign</h2>
      <form @submit.prevent="updateCampaign">
        <div class="form-group">
          <label for="campaignname">Campaign Name:</label>
          <input
            type="text"
            v-model="campaign.name"
            class="form-control"
            id="campaignname"
            required
          />
        </div>

        <div class="form-group">
          <label for="campaigndescription">Campaign Description:</label>
          <textarea
            v-model="campaign.description"
            class="form-control"
            id="campaigndescription"
            required
          ></textarea>
        </div>

        <div class="form-group">
          <label for="campaigngoals">Campaign Goals:</label>
          <textarea
            v-model="campaign.goals"
            class="form-control"
            id="campaigngoals"
            required
          ></textarea>
        </div>

        <div class="form-group">
          <label for="campaignniche">Campaign Niche:</label>
          <input
            type="text"
            v-model="campaign.niche"
            class="form-control"
            id="campaignniche"
            required
          />
        </div>

        <div class="form-group">
          <label for="campaignbudget">Campaign Budget:</label>
          <input
            type="number"
            v-model="campaign.budget"
            class="form-control"
            id="campaignbudget"
            min="0"
            required
          />
        </div>

        <div class="form-group">
          <label for="campaignvisibility">Campaign Visibility:</label>
          <div>
            <input
              type="radio"
              v-model="campaign.visibility"
              value="public"
              id="public"
            />
            <label for="public">Public</label>
            <br />
            <input
              type="radio"
              v-model="campaign.visibility"
              value="private"
              id="private"
            />
            <label for="private">Private</label>
          </div>
        </div>

        <div class="form-group">
          <label for="campaignstartdate">Campaign Start Date:</label>
          <input
            type="date"
            v-model="campaign.startDate"
            class="form-control"
            id="campaignstartdate"
            required
          />
        </div>

        <div class="form-group">
          <label for="campaignenddate">Campaign End Date:</label>
          <input
            type="date"
            v-model="campaign.endDate"
            class="form-control"
            id="campaignenddate"
            required
          />
        </div>

        <button type="submit" class="btn btn-success">Submit</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      campaign: {
        name: "",
        description: "",
        goals: "",
        niche: "",
        budget: 0,
        visibility: "public",
        startDate: "",
        endDate: "",
      },
      messages: [],
      successMessage: "",
    };
  },
  created() {
    this.fetchCampaignData();
  },
  methods: {
    async fetchCampaignData() {
      const campaignId = this.$route.params.campaign_id;
      const token = localStorage.getItem("token");
      try {
        const response = await axios.get(`/sponsor/campaign/${campaignId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.campaign = response.data.campaign;
        // Ensure dates are in the correct format
        this.campaign.startDate = this.formatDate(this.campaign.start_date);
        this.campaign.endDate = this.formatDate(this.campaign.end_date);
      } catch (error) {
        console.error("Error fetching campaign data:", error);
        this.messages.push("An error occurred while fetching campaign data.");
      }
    },
    async updateCampaign() {
      const campaignId = this.$route.params.campaign_id;
      const token = localStorage.getItem("token");
      try {
        const response = await axios.put(
          `/sponsor/editcampaign/${campaignId}`,
          this.campaign,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (response.data.success) {
          this.successMessage =
            "Campaign updated successfully ! Redirecting to Dashboard !!";
          this.messages = []; // Clear any previous error message
          setTimeout(() => {
            this.$router.push("/sponsor/dashboard");
          }, 3000);
        } else {
          this.messages = [{ message: response.data.message, type: "error" }];
        }
      } catch (error) {
        this.messages = [
          {
            message: error.response.data.message || "An error occurred",
            type: "error",
          },
        ];
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toISOString().split("T")[0]; // Format as YYYY-MM-DD
    },
  },
};
</script>

<style scoped>
.form-group {
  margin-bottom: 15px;
}

.alert {
  margin-top: 20px;
}
</style>
