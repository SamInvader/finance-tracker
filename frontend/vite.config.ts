import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite config: proxy /api to backend during dev when needed
export default defineConfig(({ command, mode }) => {
  const backend = process.env.VITE_API_URL || 'http://127.0.0.1:5001'
  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: backend,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
