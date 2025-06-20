import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [svelte()],
  server: mode === 'development' ? {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying request:', req.url)
          })
        }
      },
    },
  } : undefined,
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest-setup.js'],
    transformMode: {
      ssr: [/\.svelte$/]
    },
    deps: { inline: [/svelte/] }
  },
  resolve: process.env.VITEST
    ? {
      conditions: ['browser']
    }
    : undefined
}))