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
  
  // Default for local development
  const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  return isDev ? 'http://127.0.0.1:8000' : '';
})();

// Validate API_URL is set
if (!API_URL) {
  console.warn('⚠️ API_URL not configured. Backend calls will fail.');
  console.warn('Set VITE_API_URL environment variable in Cloudflare Pages settings.');
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API_URL };
}
