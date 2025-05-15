<script setup>
import Logout from "@/views/Logout/performLogout.vue";
</script>

<template>
  <Logout DashboardTitle="Admin Dashboard"></Logout>
  <div class="pending-sponsors container mt-5">
    <h1 class="text-center mb-4">Pending Sponsors</h1>
    <div v-if="sponsors.length" class="list-group">
      <div
        v-for="sponsor in sponsors"
        :key="sponsor.sponsor_id"
        class="list-group-item"
      >
        <h5 class="mb-1">{{ sponsor.company_name }}</h5>
        <p class="mb-1">Industry: {{ sponsor.industry }}</p>
        <button
          @click="approveSponsor(sponsor.sponsor_id)"
          class="btn btn-primary"
        >
          Approve
        </button>
      </div>
    </div>
    <p v-else>Loading or no pending sponsors...</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      sponsors: [],
    };
  },
  async created() {
    try {
      const response = await axios.get(
        "http://localhost:5000/admin/pending_sponsors",
        {
          headers: { Authorization: `Bearer ${this.$store.state.token}` },
        }
      );
      this.sponsors = response.data;
    } catch (error) {
      console.error("Failed to fetch pending sponsors:", error);
    }
  },
  methods: {
    async approveSponsor(sponsorId) {
      try {
        await axios.post(
          `http://localhost:5000/admin/approve_sponsor/${sponsorId}`,
          {},
          {
            headers: { Authorization: `Bearer ${this.$store.state.token}` },
          }
        );
        this.sponsors = this.sponsors.filter((s) => s.sponsor_id !== sponsorId);
      } catch (error) {
        console.error("Failed to approve sponsor:", error);
      }
    },
  },
};
</script>
