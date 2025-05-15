// frontend/src/store/index.js
import { createStore } from 'vuex';

export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    role: localStorage.getItem('role') || '',
    errorMessage: '',
    successMessage: '', // Add a state for success messages
  },
  mutations: {
    setToken(state, { token, role }) {
      state.token = token;
      state.role = role;
      localStorage.setItem('token', token);
      localStorage.setItem('role', role);
    },
    clearUserData(state) {
      state.token = '';
      state.role = '';
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      state.successMessage = 'Logout successfully!'; // Set success message on logout
    },
    setErrorMessage(state, message) {
      state.errorMessage = message; // Set error message
    },
    clearMessages(state) {
      state.errorMessage = '';
      state.successMessage = ''; // Clear success message
    },
  },
  actions: {
    logout({ commit }) {
      commit('clearUserData');
    },
    login({ commit }, { token, role }) {
      commit('setToken', { token, role });
    },
    setError({ commit }, message) {
      commit('setErrorMessage', message);
    },
    clearMessages({ commit }) {
      commit('clearMessages');
    },
  },
  getters: {
    isAuthenticated: state => !!state.token,
    userRole: state => state.role,
    errorMessage: state => state.errorMessage,
    successMessage: state => state.successMessage, // Add getter for success messages
  },
});
