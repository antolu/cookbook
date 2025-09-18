import '@testing-library/jest-dom'

// Mock environment variables
global.import = {
  meta: {
    env: {
      VITE_API_URL: 'http://localhost:8000/api',
    },
  },
} as any