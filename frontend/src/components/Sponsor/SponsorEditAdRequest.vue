<script setup>
import Logout from "@/views/Logout/performLogout.vue";
import axios from "axios";
</script>

<template>
  <Logout DashboardTitle="Edit Ad Request"></Logout>

  <div class="container mt-4">
    <p v-if="successMessage" class="alert alert-success mt-3">
      {{ successMessage }}
    </p>
    <div v-if="err_messages.length">
      <div class="alert alert-danger">
        <ul>
          <li v-for="message in err_messages" :key="message">{{ message }}</li>
        </ul>
      </div>
    </div>

    <form @submit.prevent="updateAdReqst">
      <div class="form-group">
        <label for="campaignname">Campaign Name:</label>
        <input
          type="text"
          class="form-control"
          v-model="ad_reqst.campaign_name"
          readonly
        />
      </div>
      <div class="form-group">
        <label for="influencername">Influencer Name:</label>
        <input
          type="text"
          class="form-control"
          v-model="ad_reqst.influencer_name"
          readonly
        />
      </div>
      <div class="form-group">
        <label for="requirements">Requirements:</label>
        <textarea
          class="form-control"
          v-model="ad_reqst.requirements"
        ></textarea>
      </div>
      <div class="form-group">
        <label for="paymentamount">Payment Amount $:</label>
        <input
          type="number"
          class="form-control"
          min="0"
          v-model="ad_reqst.payment_amount"
        />
      </div>
      <div class="form-group">
        <label for="status">Status:</label>
        <div class="form-check">
          <input
            type="radio"
            class="form-check-input"
            v-model="ad_reqst.status"
            value="pending"
            id="pending"
          />
          <label class="form-check-label" for="pending">Pending</label>
        </div>
        <div class="form-check">
          <input
            type="radio"
            class="form-check-input"
            v-model="ad_reqst.status"
            value="accepted"
            id="accepted"
          />
          <label class="form-check-label" for="accepted">Accepted</label>
        </div>
        <div class="form-check">
          <input
            type="radio"
            class="form-check-input"
            v-model="ad_reqst.status"
            value="rejected"
            id="rejected"
          />
          <label class="form-check-label" for="rejected">Rejected</label>
        </div>
      </div>
      <div class="form-group">
        <label for="messages">Message:</label>
        <textarea class="form-control" v-model="ad_reqst.messages"></textarea>
      </div>
      <button type="submit" class="btn btn-primary">Update Ad Request</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import Logout from "@/views/Logout/performLogout.vue";

export default {
  components: {
    Logout,
  },
  data() {
    return {
      ad_reqst: {
        campaign_id: "",
        campaign_name: "",
        influencer_id: "",
        influencer_name: "",
        requirements: "",
        payment_amount: "",
        status: "",
        messages: "",
      },
      err_messages: [],
      successMessage: "",
      ad_request_id: this.$route.params.ad_request_id,
    };
  },
  created() {
    this.fetchAdReqstData();
  },
  methods: {
    async fetchAdReqstData() {
      const ad_request_id = this.$route.params.ad_request_id;
      const token = localStorage.getItem("token");

      try {
        console.log(`Fetching ad request data for ID: ${ad_request_id}`);
        const response = await axios.get(`/api/advert-request/${ad_request_id}`, {
          // headers: {
          //   Authorization: `Bearer ${token}`,
          // },
          // timeout: 10000, // 10 seconds timeout
        });
        this.ad_reqst = response.data;

        // Fetching additional data
        const campaignResponse = await axios.get(
          `/api/campaign-detail/${this.ad_reqst.campaign_id}`
        );
        this.ad_reqst.campaign_name = campaignResponse.data.name;

        const influencerResponse = await axios.get(
          `/api/creator/${this.ad_reqst.influencer_id}`
        );
        this.ad_reqst.influencer_name = influencerResponse.data.name;
      } catch (error) {
        console.error("Error fetching ad request data:", error);

        if (error.response) {
          console.error("Response data:", error.response.data);
          console.error("Response status:", error.response.status);
          console.error("Response headers:", error.response.headers);
        } else if (error.request) {
          console.error("Request data:", error.request);
        } else {
          console.error("Error message:", error.message);
        }

        this.err_messages.push(
          "An error occurred while fetching ad request data."
        );
      }
    },
    async updateAdReqst() {
      const ad_request_id = this.$route.params.ad_request_id;
      const token = localStorage.getItem("token");

      try {
        const response = await axios.put(
          `/sponsor/edit_adrequest_data/${ad_request_id}`,
          this.ad_reqst,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        this.successMessage =
          "Ad Request updated Successfully ! Redirecting to Campaign (wait)";
        console.log("Ad request updated successfully:", response.data);
        setTimeout(() => {
          this.$router.push(`/sponsor/adrequest/${this.ad_reqst.campaign_id}`);
        }, 2000);
      } catch (error) {
        console.error("Error updating ad request data:", error);

        if (error.response) {
          console.error("Response data:", error.response.data);
          console.error("Response status:", error.response.status);
          console.error("Response headers:", error.response.headers);
        } else if (error.request) {
          console.error("Request data:", error.request);
        } else {
          console.error("Error message:", error.message);
        }

        this.err_messages.push(
          "An error occurred while updating ad request data."
        );
      }
    },
  },
};
</script>

<style scoped>
/* Add your custom styles here */
</style>
