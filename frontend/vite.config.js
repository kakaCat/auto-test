import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // 仅使用统一端点变量作为代理目标，未配置则回退到本地8000
  const targetBase = env.VITE_UNIFIED_API_BASE_URL || 'http://127.0.0.1:8000'

  return {
    plugins: [
      vue()
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      open: true,
      proxy: {
        // 只代理以 /api/ 开头且不包含 -management 或 -orchestration 的请求
        '^/api/(?!.*(-management|-orchestration))': {
          target: targetBase,
          changeOrigin: true
        }
      }
    },
    preview: {
      port: 5173,
      host: '0.0.0.0'
    },
    build: {
      outDir: 'dist',
      sourcemap: false
    }
  }
})