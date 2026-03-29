import '@testing-library/jest-dom';

// Mock environment variables
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).import = {
  meta: {
    env: {
      VITE_API_URL: 'http://localhost:8000/api',
    },
  },
} satisfies Record<string, unknown>;
