import axios from 'axios';
const API_BASE_URL = 'http://localhost:5000';
export const ApiCall = (token , api_route) => {
  return axios.post(`${API_BASE_URL}/${api_route}`, {
    headers : { Authorization: `Bearer ${token}` }
  });
};
