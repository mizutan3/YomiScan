// src/services/api.ts
import axios from 'axios';

export const API_BASE_URL = "http://192.168.0.104:5000"; // Local

export const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });
