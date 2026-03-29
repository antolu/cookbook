/**
 * Application configuration
 *
 * Supports two deployment modes:
 * - Development: Standalone app with no authentication
 * - Integrated: Subapp within haochen.lu with shared JWT authentication
 */

export const config = {
  // API endpoint URL
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',

  // App mode: development (standalone) or integrated (subapp)
  appMode: (import.meta.env.VITE_APP_MODE as 'development' | 'integrated') || 'development',

  // Check if running in integrated mode
  isIntegrated: import.meta.env.VITE_APP_MODE === 'integrated',

  // Check if running in development mode
  isDevelopment: import.meta.env.VITE_APP_MODE !== 'integrated',
} as const;

export default config;
