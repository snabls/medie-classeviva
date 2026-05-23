import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'https://web.spaggiari.eu',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/rest/v1'),
        // Vite forzerà questi header su TUTTE le chiamate, aggirando il browser!
        headers: {
          'User-Agent': 'zorro/1.0',
          'Z-Dev-Apikey': '+zorro+'
        }
      }
    }
  }
})