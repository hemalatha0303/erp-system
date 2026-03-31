// API Configuration - Centralized
// This file defines the backend API URL used by all pages

const API_URL = (() => {
  // Static hosting-friendly overrides (no module syntax so this file stays parseable)
  if (typeof globalThis !== "undefined") {
    if (globalThis.ERP_API_URL) {
      return globalThis.ERP_API_URL;
    }
    if (globalThis.ERP_CONFIG && globalThis.ERP_CONFIG.API_URL) {
      return globalThis.ERP_CONFIG.API_URL;
    }
  }

  if (typeof window !== "undefined") {
    const meta = document.querySelector('meta[name="erp-api-url"]');
    if (meta && meta.content) {
      return meta.content;
    }
  }
  
  // Fallback to localStorage (user can set it manually if needed)
  const stored = localStorage.getItem("API_URL");
  if (stored) {
    return stored;
  }
  
  // Production Railway backend URL
  const isProduction = window.location.hostname === "erp-system.hemalatha0303.workers.dev" ||
                       window.location.hostname.includes("pages.dev");
  if (isProduction) {
    return "https://erp-system-production-4ede.up.railway.app";
  }
  
  // Default for local development
  const isDev = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  return isDev ? "http://127.0.0.1:8000" : "https://erp-system-production-4ede.up.railway.app";
})();

console.log("API Configuration loaded");
console.log("Backend URL:", API_URL);

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API_URL };
}
