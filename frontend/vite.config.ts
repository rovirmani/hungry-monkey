import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
<<<<<<< HEAD
  // Load env file from root directory
  const env = loadEnv(mode, '../', ['VITE_'])
=======
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), ['VITE_'])
  
  console.log('🔧 Building with env:', {
    mode,
    apiUrl: env.VITE_API_URL,
    hasClerkKey: !!env.VITE_CLERK_PUBLISHABLE_KEY
  })
>>>>>>> origin
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    define: {
      'import.meta.env.VITE_CLERK_PUBLISHABLE_KEY': JSON.stringify(env.VITE_CLERK_PUBLISHABLE_KEY),
<<<<<<< HEAD
=======
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL),
>>>>>>> origin
    },
    optimizeDeps: {
      exclude: ['lucide-react'],
    },
<<<<<<< HEAD
=======
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
          },
        },
      },
    },
>>>>>>> origin
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
<<<<<<< HEAD
          rewrite: (path) => path.replace(/^\/api/, ''),
=======
>>>>>>> origin
        },
      },
    },
  }
})
