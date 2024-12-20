import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), ['VITE_'])
  
  console.log('🔧 Building with env:', {
    mode,
    apiUrl: env.VITE_API_URL,
    hasClerkKey: !!env.VITE_CLERK_PUBLISHABLE_KEY
  })
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'lodash': 'lodash-es'
      },
    },
    define: {
      'import.meta.env.VITE_CLERK_PUBLISHABLE_KEY': JSON.stringify(env.VITE_CLERK_PUBLISHABLE_KEY),
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL),
    },
    optimizeDeps: {
      exclude: ['lucide-react'],
      include: ['lodash/debounce']
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
          },
        },
        external: [],
      },
    },
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
