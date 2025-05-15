<script setup>
import Logout from "@/views/Logout/performLogout.vue";
</script>

<template>
  <Logout DashboardTitle="Search Influencers"></Logout>
  <div class="container mt-5">
    <h2 class="text-center mb-4">Influencers List</h2>

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
        <option value="reach-asc">Reach (Ascending)</option>
        <option value="reach-desc">Reach (Descending)</option>
      </select>
    </div>

    <!-- Influencers Table -->
    <table class="table table-hover mt-3">
      <thead class="thead-dark">
        <tr>
          <th>Name</th>
          <th>Niche</th>
          <th>Category</th>
          <th>Reach</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="influencer in filteredAndSortedInfluencers"
          :key="influencer.influencer_id"
        >
          <td>{{ influencer.name }}</td>
          <td>{{ influencer.niche }}</td>
          <td>{{ influencer.category }}</td>
          <td>{{ influencer.reach }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      influencers: [],
      searchQuery: "",
      sortKey: "",
    };
  },
  computed: {
    filteredAndSortedInfluencers() {
      // Filter based on search query
      let filtered = this.influencers.filter((influencer) => {
        const query = this.searchQuery.toLowerCase();
        return (
          influencer.name.toLowerCase().includes(query) ||
          influencer.niche.toLowerCase().includes(query)
        );
      });

      // Sort based on sortKey
      if (this.sortKey.includes("name")) {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
      } else if (this.sortKey.includes("reach")) {
        filtered.sort((a, b) => a.reach - b.reach);
      }

      // Reverse order if descending
      if (this.sortKey.endsWith("desc")) {
        filtered.reverse();
      }

      return filtered;
    },
  },
  created() {
    this.fetchInfluencers();
  },
  methods: {
    async fetchInfluencers() {
      try {
        const response = await axios.get(
          "http://127.0.0.1:5000/api/creators"
        );
        this.influencers = response.data;
      } catch (error) {
        console.error("Error fetching influencers:", error);
      }
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: auto;
}

.table-hover tbody tr:nth-child(even) {
  background-color: #b2694f; /* Light gray color for even rows */
}

.table-hover tbody tr:nth-child(odd) {
  background-color: #6d54a4; /* White color for odd rows */
}

.table-hover tbody tr:hover {
  background-color: #1fa9be; /* Light blue on hover */
}

.thead-dark th {
  background-color: #343a40;
  color: white;
}

.form-group {
  margin-bottom: 1.5rem;
}

.text-center {
  text-align: center;
}
</style>
