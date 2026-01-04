/**
 * API client with axios for backend communication.
 * Includes JWT token interceptor, error handling, and retry logic.
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
  timeout: 30000, // 30 seconds (increased for Neon cold starts)
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

// Retry logic for failed requests (handles cold starts)
const MAX_RETRIES = 2;
const RETRY_DELAY = 1000; // 1 second

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { _retryCount?: number };

    // Handle 401 errors
    if (error.response?.status === 401) {
      console.error("API 401 Unauthorized:", error.response.data);
      return Promise.reject(error);
    }

    // Retry on timeout or 5xx errors (likely cold start issues)
    const shouldRetry =
      (error.code === 'ECONNABORTED' || // timeout
       error.code === 'ERR_NETWORK' || // network error
       (error.response?.status && error.response.status >= 500)) &&
      (!config._retryCount || config._retryCount < MAX_RETRIES);

    if (shouldRetry && config) {
      config._retryCount = (config._retryCount || 0) + 1;
      console.log(`Retrying request (attempt ${config._retryCount}/${MAX_RETRIES})...`);

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * config._retryCount!));

      return apiClient.request(config);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
