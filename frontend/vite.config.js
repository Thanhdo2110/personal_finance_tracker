import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3001,
    host: true ,
    proxy: {
      '/api': {
        target: 'http://finance-tracker-backend-dev:5001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});import { defineConfig } from 'vite';

export default defineConfig({

    server: {

        host: '0.0.0.0',

        port: 3001,

        proxy: {

            '/api': {

                target: process.env.VITE_API_URL || 'http://localhost:5001',

                changeOrigin: true,

                secure: false

            }

        }

    },

    build: {

        outDir: 'dist',

        sourcemap: false

    }

});
