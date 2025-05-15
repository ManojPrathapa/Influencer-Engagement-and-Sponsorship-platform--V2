<script setup>
import Logout from "@/views/Logout/performLogout.vue";
</script>

<template>
  <div>
    <Logout DashboardTitle="New Ad Request"></Logout>
  </div>
  <p v-if="successMessage" class="alert alert-success mt-3">
    {{ successMessage }}
  </p>
  <div class="container mt-5">
    <h2>Add Ad Request Data</h2>
    <form @submit.prevent="submitAdRequest">
      <div class="form-group">
        <label for="campaign">Campaign</label>
        <select
          id="campaign"
          v-model="selectedCampaign"
          class="form-control"
          required
        >
          <option disabled value="">Select Campaign</option>
          <option
            v-for="campaign in campaigns"
            :key="campaign.campaign_id"
            :value="campaign.campaign_id"
          >
            {{ campaign.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="influencer">Influencer</label>
        <select
          id="influencer"
          v-model="selectedInfluencer"
          class="form-control"
          required
        >
          <option disabled value="">Select Influencer</option>
          <option
            v-for="influencer in influencers"
            :key="influencer.influencer_id"
            :value="influencer.influencer_id"
          >
            {{ influencer.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="requirements">Requirements</label>
        <input
          v-model="requirements"
          type="text"
          id="requirements"
          class="form-control"
          required
        />
      </div>

      <div class="form-group">
        <label for="message">Message</label>
        <input
          v-model="message"
          type="text"
          id="message"
          class="form-control"
          required
        />
      </div>

      <div class="form-group">
        <label for="payment_amount">Payment Amount: $</label>
        <input
          v-model="paymentAmount"
          type="number"
          min="0"
          id="payment_amount"
          class="form-control"
          required
        />
      </div>

      <button type="submit" class="btn btn-primary">Submit</button>
    </form>

    <div v-if="messages.length" class="alert alert-danger mt-3">
      <ul>
        <li v-for="message in messages" :key="message">{{ message }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      campaigns: [], // Fix here
      influencers: [],
      selectedCampaign: "",
      selectedInfluencer: "",
      requirements: "",
      message: "",
      paymentAmount: 0,
      messages: [],
      successMessage: "",
    };
  },
  created() {
    this.fetchCampaigns();
    this.fetchInfluencers();
  },
  methods: {
    async fetchCampaigns() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/campaigns-list");
        if (response.data.success) {
          this.campaigns = response.data.campaigns; // Fix here
        } else {
          this.messages.push("No campaigns available.");
        }
      } catch (error) {
        console.error("Error fetching campaigns:", error);
        this.messages.push("Error fetching campaigns.");
      }
    },
    async fetchInfluencers() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.messages.push("Authorization token is missing.");
        return;
      }

      try {
        const response = await axios.get(
          "http://127.0.0.1:5000/api/creators"
        );
        this.influencers = response.data;
      } catch (error) {
        console.error("Error fetching influencers:", error);
        this.messages.push("Error fetching influencers.");
      }
    },
    async submitAdRequest() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.messages.push("Authorization token is missing.");
        return;
      }

      try {
        const data = {
          campaign_id: this.selectedCampaign,
          influencer_id: this.selectedInfluencer,
          requirements: this.requirements,
          payment_amount: this.paymentAmount,
          messages: this.message,
        };

        const response = await axios.post(
          "http://127.0.0.1:5000/sponsor/add_adRequest_data",
          data,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          this.successMessage =
            "Ad request added successfully! Redirecting to Dashboard ! (wait pls :) )";
          setTimeout(() => {
            this.$router.push(`/sponsor/adrequest/${this.selectedCampaign}`);
          }, 3000);
        } else {
          this.messages = [response.data.message];
        }
      } catch (error) {
        console.error("Error submitting ad request:", error);
        this.messages = [
          error.response?.data.message ||
            "An error occurred while adding the ad request.",
        ];
      }
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: auto;
}
</style>
