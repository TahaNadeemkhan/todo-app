/**
 * API client with axios for backend communication.
 * T062-T063: Supports Dapr Service Invocation for mTLS-secured calls.
 * Includes JWT token interceptor, error handling, and retry logic.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAuthToken } from "./auth-client";

// T062: Dapr Service Invocation support
// When NEXT_PUBLIC_USE_DAPR=true, calls go through Dapr sidecar
// Format: http://localhost:3500/v1.0/invoke/{app-id}/method/{method-name}
const USE_DAPR = process.env.NEXT_PUBLIC_USE_DAPR === "true";
const DAPR_HTTP_PORT = process.env.NEXT_PUBLIC_DAPR_HTTP_PORT || "3500";
const BACKEND_APP_ID = process.env.NEXT_PUBLIC_BACKEND_APP_ID || "backend-api";

// Default to 127.0.0.1 to avoid localhost IPv4/IPv6 resolution issues
// Use leading slash in browser to leverage root-relative paths (e.g. /api/...)
const DIRECT_API_URL = typeof window !== "undefined" 
  ? "/" 
  : (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000");

// T062: Determine base URL based on Dapr configuration
const API_BASE_URL = USE_DAPR
  ? `http://localhost:${DAPR_HTTP_PORT}/v1.0/invoke/${BACKEND_APP_ID}/method`
  : DIRECT_API_URL;

console.log(`API Client initialized: USE_DAPR=${USE_DAPR}, BASE_URL=${API_BASE_URL}`);

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
