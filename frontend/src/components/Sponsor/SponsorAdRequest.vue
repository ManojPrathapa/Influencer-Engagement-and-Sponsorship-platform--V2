<script setup>
import Logout from "@/views/Logout/performLogout.vue";
import axios from "axios";
import { Modal } from "bootstrap";
</script>

<template>
  <Logout DashboardTitle="Ad Requests"></Logout>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="ml-auto">
      <button class="btn btn-success mb-3" @click="addAdRequest(campaign_id)">
        + New AD request
      </button>
    </div>
  </nav>
  <div class="container mt-5">
    <h2 class="text-center mb-4">{{ campaign.name || "Campaign Details" }}</h2>
    <div v-if="messages.length" class="alert alert-danger">
      <ul>
        <li v-for="message in messages" :key="message">{{ message }}</li>
      </ul>
    </div>
    <div v-if="adRequests.length === 0" class="text-center">
      <p>No ad requests found for this campaign.</p>
    </div>
    <div v-else>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th>Influencer</th>
            <th>Requirements</th>
            <th>Payment Amount</th>
            <th>Status</th>
            <th>Messages</th>
            <th>Negotiated Amount</th>
            <th>Negotiated Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in adRequests" :key="request.ad_request_id">
            <td>{{ request.influencer.name }}</td>
            <td>{{ request.requirements }}</td>
            <td>{{ formatCurrency(request.payment_amount) }}</td>
            <td>{{ request.status }}</td>
            <td>{{ request.messages }}</td>
            <td>{{ formatCurrency(request.negotiation.negotiated_amount) }}</td>
            <td>{{ request.negotiation.negotiation_status }}</td>

            <td>
              <button
                class="btn btn-primary btn-sm"
                @click="editAdRequest(request.ad_request_id)"
              >
                Edit
              </button>
              <button
                class="btn btn-danger btn-sm"
                @click="confirmDelete(request.ad_request_id)"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Confirmation Modal -->
  <div
    class="modal fade"
    id="confirmDeleteModal"
    tabindex="-1"
    aria-labelledby="confirmDeleteModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="confirmDeleteModalLabel">
            Confirm Deletion
          </h5>

          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <h5>Are you sure you want to delete this ad request?</h5>
          <br />

          <p>
            <strong>Requirements :</strong> {{ adRequestDelData.requirements }}
          </p>
          <p>
            <strong>Payment Amount :</strong>
            {{ formatCurrency(adRequestDelData.payment_amount) }}
          </p>
          <p><strong>Messages :</strong> {{ adRequestDelData.messages }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">
            Close
          </button>
          <button type="button" class="btn btn-danger" @click="deleteAdReqst">
            Delete
          </button>
          <!-- <button class="btn btn-danger btn-sm" @click="confirmDelete(request.ad_request_id)">Delete</button> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      adRequests: [],
      campaign: {},
      messages: [],
      campaign_id: "",
      adRequestToDelete: null,
      adRequestDelData: [],
    };
  },
  created() {
    this.fetchAdRequests();
  },
  methods: {
    async fetchAdRequests() {
      const campaignId = this.$route.params.campaign_id;
      // console.log("Cmap ID" , campaignId);
      this.campaign_id = campaignId;
      const token = localStorage.getItem("token");

      if (!token) {
        this.messages = ["Authorization token is missing."];
        return;
      }

      try {
        const response = await axios.get(
          `/sponsor/adrequest_data/${campaignId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 200) {
          // console.log(response.data)

          this.adRequests = response.data.adrequests;
          this.campaign =
            this.adRequests.length > 0 ? this.adRequests[0].campaign : {};
          this.messages = [];
        } else {
          this.messages = [response.data.message || "Error fetching data"];
        }
      } catch (error) {
        if (error.response) {
          // The request was made, and the server responded with a status code
          // that falls out of the range of 2xx
          this.messages.push({
            message: error.response.data.message || "Error fetching data",
            type: "error",
          });
        } else if (error.request) {
          // The request was made but no response was received
          this.messages.push({
            message: "No response received from server.",
            type: "error",
          });
        } else {
          // Something happened in setting up the request that triggered an Error
          this.messages.push({
            message: "An error occurred: " + error.message,
            type: "error",
          });
        }
      }
    },
    formatCurrency(amount) {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
    },
    addAdRequest(adRequestId) {
      window.location.href = `/sponsor/add_adRequest_data/${adRequestId}`;
    },
    editAdRequest(adRequestId) {
      // Navigate to the edit page with the ad request ID
      window.location.href = `/sponsor/edit_adrequest_data/${adRequestId}`;
    },
    async confirmDelete(adRequestId) {
      this.adRequestToDelete = adRequestId;
      const token = localStorage.getItem("token");
      const res = await axios.get(`/api/advert-request/${adRequestId}`, );
      this.adRequestDelData = res.data;

      // Show the modal
      const deleteModal = new Modal(
        document.getElementById("confirmDeleteModal")
      );

      deleteModal.show();
    },
    async deleteAdReqst() {
      const ad_request_id = this.adRequestToDelete;
      const token = localStorage.getItem("token");

      try {
        const response = await axios.delete(
          `/sponsor/delete_adrequest_data/${ad_request_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        this.successMessage = response.data.message;
        console.log("Ad request deleted successfully:", response.data);
        // Close the modal and refresh the ad requests list
        const deleteModal = new Modal(
          document.getElementById("confirmDeleteModal")
        );
        deleteModal.hide();
        this.fetchAdRequests();
      } catch (error) {
        console.error("Error deleting ad request data:", error);

        if (error.response) {
          console.error("Response data:", error.response.data);
          console.error("Response status:", error.response.status);
          console.error("Response headers:", error.response.headers);
        } else if (error.request) {
          console.error("Request data:", error.request);
        } else {
          console.error("Error message:", error.message);
        }

        this.messages.push("An error occurred while deleting ad request data.");
      }
    },
  },
};
</script>

<style scoped>
.table th,
.table td {
  vertical-align: middle;
}
</style>
