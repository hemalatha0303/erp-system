// API Configuration - Centralized
// This file defines the backend API URL used by all pages

const API_URL = (() => {
  // Try to get from Cloudflare environment variable first
  if (typeof import !== 'undefined' && import.meta?.env?.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Fallback to localStorage (user can set it manually if needed)
  const stored = localStorage.getItem('API_URL');
  if (stored) {
    return stored;
  }
  
  // Production Railway backend URL
  const isProduction = window.location.hostname === 'erp-system.hemalatha0303.workers.dev' || 
                       window.location.hostname.includes('pages.dev');
  if (isProduction) {
    return 'https://erp-system-production-4ede.up.railway.app';
  }
  
  // Default for local development
  const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  return isDev ? 'http://127.0.0.1:8000' : 'https://erp-system-production-4ede.up.railway.app';
})();

console.log('✅ API Configuration loaded');
console.log('Backend URL:', API_URL);

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API_URL };
}
