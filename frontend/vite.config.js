import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const DJANGO = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Только API и медиафайлы идут в Django
      '/api': { target: DJANGO, changeOrigin: true, secure: false },
      '/media': { target: DJANGO, changeOrigin: true, secure: false },
      '/static': { target: DJANGO, changeOrigin: true, secure: false },
      // /admin/* — НЕ проксируем, это маршруты React Router
    },
  },
})
