<script setup>
import Logout from "@/views/Logout/performLogout.vue";
import axios from "axios";
import { jwtDecode } from "jwt-decode";
</script>

<template>
  <div>
    <Logout DashboardTitle="Sponsor Manage Campaign"></Logout>
  </div>

  <div class="container">
    <p v-if="successMessage" class="alert alert-success mt-3">
      {{ successMessage }}
    </p>
    <div v-if="messages.length">
      <div class="alert alert-danger">
        <ul>
          <li v-for="message in messages" :key="message">{{ message }}</li>
        </ul>
      </div>
    </div>

    <h2>Add New Campaign</h2>
    <form @submit.prevent="submitCampaign">
      <div class="form-group">
        <label for="campaignname">Campaign Name:</label>
        <input
          type="text"
          class="form-control"
          id="campaignname"
          v-model="campaign.name"
          required
        />
      </div>

      <div class="form-group">
        <label for="campaigndescription">Campaign Description:</label>
        <textarea
          class="form-control"
          id="campaigndescription"
          v-model="campaign.description"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label for="campaigngoals">Campaign Goals:</label>
        <textarea
          class="form-control"
          id="campaigngoals"
          v-model="campaign.goals"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label for="campaignniche">Campaign Niche:</label>
        <input
          type="text"
          class="form-control"
          id="campaignniche"
          v-model="campaign.niche"
          required
        />
      </div>

      <div class="form-group">
        <label for="campaignbudget">Campaign Budget:</label>
        <input
          type="number"
          step="1"
          min="0"
          class="form-control"
          id="campaignbudget"
          v-model="campaign.budget"
          required
        />
      </div>

      <div class="form-group">
        <label for="campaignvisibility">Campaign Visibility:</label><br />
        <div class="form-check form-check-inline">
          <input
            class="form-check-input"
            type="radio"
            id="public"
            value="public"
            v-model="campaign.visibility"
            required
          />
          <label class="form-check-label" for="public">Public</label>
        </div>
        <div class="form-check form-check-inline">
          <input
            class="form-check-input"
            type="radio"
            id="private"
            value="private"
            v-model="campaign.visibility"
            required
          />
          <label class="form-check-label" for="private">Private</label>
        </div>
      </div>

      <div class="form-group">
        <label for="campaignstartdate">Campaign Start Date:</label>
        <input
          type="date"
          class="form-control"
          id="campaignstartdate"
          v-model="campaign.startDate"
          required
        />
      </div>

      <div class="form-group">
        <label for="campaignenddate">Campaign End Date:</label>
        <input
          type="date"
          class="form-control"
          id="campaignenddate"
          v-model="campaign.endDate"
          required
        />
      </div>

      <button type="submit" class="btn btn-success">Submit</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  name: "AddCampaign",
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
  methods: {
    async submitCampaign() {
      try {
        const response = await axios.post(
          "/sponsor/addcampaign",
          this.campaign,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        if (response.data.success) {
          // Handle success (e.g., navigate to another page, clear the form, etc.)
          this.successMessage =
            "Campaign Added successfully ! Redirecting to Dashboard !!";
          this.messages = []; // Clear any previous error message
          setTimeout(() => {
            this.$router.push("/sponsor/dashboard");
          }, 3000);
        } else {
          // Handle error messages
          this.messages = response.data.messages || ["An error occurred"];
        }
      } catch (error) {
        console.error("Error submitting campaign:", error);
        this.messages = ["An error occurred"];
      }
    },
  },
};
</script>

<style scoped>
body {
  background-color: #f8f9fa;
}
.container {
  margin-top: 50px;
}
.navbar-custom {
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 15px;
}
</style>
