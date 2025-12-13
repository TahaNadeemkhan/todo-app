/**
 * API client with axios for backend communication.
 * Includes JWT token interceptor and error handling.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAuthToken } from "./auth-client";

// Default to 127.0.0.1 to avoid localhost IPv4/IPv6 resolution issues
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor: Attach JWT token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = await getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle 401 errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Redirect to login on authentication failure
      // DISABLED to prevent infinite loops during debugging
      // if (typeof window !== "undefined") {
      //   window.location.href = "/login";
      // }
      console.error("API 401 Unauthorized:", error.response.data);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
