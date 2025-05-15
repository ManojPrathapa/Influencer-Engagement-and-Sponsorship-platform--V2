import { createRouter, createWebHistory } from "vue-router";

import store from "@/store";

import IndexView from "@/views/IndexView.vue";
import NotFound from "@/views/NotFound/NotFound.vue";
import AdminLogin from "@/views/Admin/AdminLogin.vue";
import AdminDashboard from "@/views/Admin/AdminDashboard.vue";
import AdminRegistration from "@/views/Admin/AdminRegistration.vue";
import AdminPendingSponsors from "@/views/Admin/AdminPendingSponsors.vue";
import SponsorLogin from "@/components/Sponsor/SponsorLogin.vue";
import SponsorRegistration from "@/components/Sponsor/SponsorRegistration.vue";
import SponsorDashboard from "@/components/Sponsor/SponsorDashboard.vue";
import Logout from "@/views/Logout/performLogout.vue";
import SponsorAddCampaign from "@/components/Sponsor/SponsorAddCampaign.vue";
import SponsorEditCampaign from "@/components/Sponsor/SponsorEditCampaign.vue";
import SponsorAdRequest from "@/components/Sponsor/SponsorAdRequest.vue";
import SponsorAddadd_adRequest_data from "@/components/Sponsor/SponsorAddadd_adRequest_data.vue";
import SearchInfluencer from "@/components/Sponsor/SearchInfluencer.vue";
import SponsorEditAdRequest from "@/components/Sponsor/SponsorEditAdRequest.vue";

import InfluLogin from "@/components/Influencer/InfluLogin.vue";
import InfluDashboard from "@/components/Influencer/InfluDashboard.vue";
import InflueRegister from "@/components/Influencer/InflueRegister.vue";
import InfluacceptAdRequest from "@/components/Influencer/InfluAcceptAdRequest.vue";
import InfluRejectAdRequest from "@/components/Influencer/InfluRejectAdRequest.vue";
import InfluNegoAdRequest from "@/components/Influencer/influNegoAdRequest.vue";
import SeachPubCamp from "@/components/Influencer/SeachPubCamp.vue";
import InfluProfile from "@/components/Influencer/InfluProfile.vue";

const routes = [
  { path: "/", name: "Home", component: IndexView },
  { path: "/:pathMatch(.*)*", name: "NotFound", component: NotFound },
  { path: "/logout", name: "Logout", component: Logout },

  // Admin paths
  {
    path: "/admin/login",
    name: "AdminLogin",
    component: AdminLogin,
  },
  {
    path: "/admin/register",
    name: "AdminRegister",
    component: AdminRegistration,
  },
  {
    path: "/admin/dashboard",
    name: "AdminDashboard",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/admin/pending_sponsors",
    name: "AdminPendingSponsors",
    component: AdminPendingSponsors,
    meta: { requiresAuth: true, role: "admin" },
  },

  // Sponsor paths
  {
    path: "/sponsor/login",
    name: "SponsorLogin",
    component: SponsorLogin,
  },
  {
    path: "/sponsor/register",
    name: "SponsorRegistration",
    component: SponsorRegistration,
  },
  {
    path: "/sponsor/dashboard",
    name: "SponsorDashboard",
    component: SponsorDashboard,
    meta: { requiresAuth: true, role: "sponsor" },
  },
  {
    path: "/sponsor/addcampaign",
    name: "SponsorAddCampaign",
    component: SponsorAddCampaign,
    meta: { requiresAuth: true, role: "sponsor" },
  },
  {
    path: "/sponsor/editcampaign/:campaign_id",
    name: "SponsorEditCampaign",
    component: SponsorEditCampaign,
    meta: { requiresAuth: true, role: "sponsor" },
  },
  {
    path: "/sponsor/adrequest/:campaign_id",
    name: "SponsorAdRequest",
    component: SponsorAdRequest,
    meta: { requiresAuth: true, role: "sponsor" },
  },
  {
    path: "/sponsor/add_adRequest_data/:campaign_id",
    name: "SponsorAddAdRequestData",
    component: SponsorAddadd_adRequest_data,
    meta: { requiresAuth: true, role: "sponsor" },
  },
  {
    path: "/sponsor/search_influencer",
    name: "SearchInfluencer",
    component: SearchInfluencer,
    meta: { requiresAuth: true, role: "sponsor" },
  },
  {
    path: "/sponsor/edit_adrequest_data/:ad_request_id",
    name: "SponsorEditAdRequest",
    component: SponsorEditAdRequest,
    meta: { requiresAuth: true, role: "sponsor" },
  },

  // Influencer paths
  {
    path: "/influencer/login",
    name: "InfluLogin",
    component: InfluLogin,
  },
  {
    path: "/influencer/register",
    name: "InflueRegister",
    component: InflueRegister,
  },
  {
    path: "/influencer/dashboard",
    name: "InfluDashboard",
    component: InfluDashboard,
    meta: { requiresAuth: true, role: "influencer" },
  },

  {
    path: "/influencer/acceptAdRequest/:ad_request_id",
    name: "InfluAcceptAdRequest",
    component: InfluacceptAdRequest,
    meta: { requiresAuth: true, role: "influencer" },
  },

  {
  path: "/influencer/rejectAdRequest/:ad_request_id",
  name: "InfluRejectAdRequest",
  component: InfluRejectAdRequest,
  meta: { requiresAuth: true, role: "influencer" },
  },

  {
    path: "/influencer/negoAdRequest/:ad_request_id",
    name: "InfluNegoAdRequest",
    component: InfluNegoAdRequest,
    meta: { requiresAuth: true, role: "influencer" },
  },
  {
    path: "/influencer/search_pubcamp",
    name: "SeachPubCamp",
    component: SeachPubCamp,
    meta: { requiresAuth: true, role: "influencer" },
  },
  {
    path: "/influencer/profile",
    name: "InfluProfile",
    component: InfluProfile,
    meta: { requiresAuth: true, role: "influencer" },
  },




];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;
  const userRole = store.state.token
    ? JSON.parse(atob(store.state.token.split(".")[1])).role
    : null;


  // Redirect to dashboard if already authenticated and accessing a login page
  if (isAuthenticated && to.path.includes('/login')) {
    if (userRole === 'admin') {
      next({ name: 'AdminDashboard' });
    } else if (userRole === 'sponsor') {
      next({ name: 'SponsorDashboard' });
    } else if (userRole === 'influencer') {
      next({ name: 'InfluDashboard' });
    } else {
      next({ name: 'Home' });
    }
    return;
  }


  if (to.meta.requiresAuth && (!isAuthenticated || userRole !== to.meta.role)) {
    store.commit(
      "setErrorMessage",
      "You cannot access this page. Please log in!"
    );
    next({ name: "Home" }); // Redirect to home 
  } else if (to.meta.role && userRole !== to.meta.role) {
    // User does not have the required role
    store.commit(
      "setErrorMessage",
      "You do not have permission to access this page."
    );
    next({ name: "Home" }); // Redirect to a 404 page or unauthorized page
  } else {
    next();
  }
});

export default router;
