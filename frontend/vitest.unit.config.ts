/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    testTimeout: 10000, // Increased timeout for async operations
    hookTimeout: 10000, // Increased hook timeout for async operations
    // NO globalSetup - this eliminates E2E build overhead
    include: [
      // Only include unit tests, exclude E2E tests
      'src/test/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'src/test/components/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'src/test/hooks/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'src/test/photo-booth/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'src/test/photo-booth/integration/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
    exclude: [
      // Explicitly exclude E2E tests to prevent accidental execution
      'node_modules/**',
      'src/test/e2e/**',
      'src/test/photo-booth/e2e/**',
      'src/test/**/e2e/**'
    ],
    deps: {
      optimizer: {
        web: {
          include: ['@testing-library/user-event', '@testing-library/react', '@testing-library/dom']
        }
      }
    },
    coverage: {
      provider: 'v8',
      reporter: ['text'],
      exclude: [
        'node_modules/**',
        'dist/**',
        '.astro/**',
        'src/test/**',
        '**/*.d.ts',
        '**/*.config.*',
        'scripts/**'
      ]
    }
  },
  resolve: {
    alias: {
      '@/components': resolve(__dirname, './src/layouts/components'),
      '@/shortcodes': resolve(__dirname, './src/layouts/shortcodes'),
      '@/helpers': resolve(__dirname, './src/layouts/helpers'),
      '@/partials': resolve(__dirname, './src/layouts/partials'),
      '@/lib': resolve(__dirname, './src/lib'),
      '@/config': resolve(__dirname, './src/config'),
      '@/layouts': resolve(__dirname, './src/layouts'),
      '@/hooks': resolve(__dirname, './src/hooks'),
      '@/types': resolve(__dirname, './src/types'),
      '@/services': resolve(__dirname, './src/services'),
      '@': resolve(__dirname, './src')
    }
  }
});
