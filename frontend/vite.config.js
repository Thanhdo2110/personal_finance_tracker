import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://finance-backend:5001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
