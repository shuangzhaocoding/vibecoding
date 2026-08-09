import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // 反代 / 自定义域名访问（如 vibecoding.yugongcoding.com）
    allowedHosts: true,
    // Docker 经 nginx:80 反代时，把 HMR WebSocket 指到对外端口
    hmr: process.env.VITE_HMR_CLIENT_PORT
      ? { clientPort: Number(process.env.VITE_HMR_CLIENT_PORT) }
      : undefined,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY || 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
