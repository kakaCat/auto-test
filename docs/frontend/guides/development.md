# AI自动化测试系统 - 开发环境配置和启动指南

## 📋 目录

1. [环境要求](#环境要求)
2. [项目初始化](#项目初始化)
3. [开发环境配置](#开发环境配置)
4. [启动和运行](#启动和运行)
5. [构建和部署](#构建和部署)
6. [开发工具配置](#开发工具配置)
7. [常见问题解决](#常见问题解决)
8. [开发规范](#开发规范)

## 🔧 环境要求

### 基础环境
- **Node.js**: >= 16.0.0 (推荐使用 LTS 版本)
- **npm**: >= 8.0.0 (或使用 yarn >= 1.22.0)
- **Git**: >= 2.20.0

### 推荐开发工具
- **IDE**: Visual Studio Code
- **浏览器**: Chrome >= 90 或 Firefox >= 88
- **终端**: 支持 ANSI 颜色的现代终端

### 系统兼容性
- **Windows**: 10/11
- **macOS**: 10.15+
- **Linux**: Ubuntu 18.04+ / CentOS 7+

## 🚀 项目初始化

### 1. 克隆项目
```bash
# 克隆项目仓库
git clone <repository-url>
cd auto-test/frontend

# 或者如果已经在项目目录中
cd frontend
```

### 2. 安装依赖
```bash
# 使用 npm 安装依赖
npm install

# 或使用 yarn
yarn install

# 如果遇到网络问题，可以使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

### 3. 验证安装
```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 检查项目依赖
npm list --depth=0
```

## ⚙️ 开发环境配置

### 1. 环境变量配置

创建环境变量文件（可选）：
```bash
# 在项目根目录创建 .env.local 文件
touch .env.local
```

`.env.local` 文件内容示例：
```env
# 开发环境配置
VITE_APP_TITLE=AI自动化测试系统
VITE_APP_VERSION=1.0.0

# API 配置
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=true

# 第三方服务配置
VITE_SENTRY_DSN=your-sentry-dsn
VITE_GA_TRACKING_ID=your-ga-id
```

### 2. Vite 配置详解

**文件位置**: `vite.config.js`

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  // 插件配置
  plugins: [
    vue()  // Vue 3 支持
  ],
  
  // 路径别名配置
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),      // @/ 指向 src/
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@styles': resolve(__dirname, 'src/styles')
    }
  },
  
  // 开发服务器配置
  server: {
    port: 3000,           // 开发端口
    host: '0.0.0.0',      // 允许外部访问
    open: true,           // 自动打开浏览器
    cors: true,           // 启用 CORS
    
    // API 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 后端服务地址
        changeOrigin: true,               // 改变请求源
        rewrite: (path) => path.replace(/^\/api/, '')  // 重写路径
      }
    }
  },
  
  // 构建配置
  build: {
    outDir: 'dist',       // 输出目录
    sourcemap: false,     // 生产环境不生成 sourcemap
    minify: 'terser',     // 使用 terser 压缩
    chunkSizeWarningLimit: 1000,  // chunk 大小警告限制
    
    // Rollup 配置
    rollupOptions: {
      output: {
        // 手动分包
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'utils': ['axios', 'dayjs', 'lodash-es']
        }
      }
    }
  }
})
```

### 3. 自动导入配置

项目使用 `unplugin-auto-import` 和 `unplugin-vue-components` 实现自动导入：

**自动导入的 API**:
- Vue 3 Composition API (ref, reactive, computed, watch 等)
- Vue Router (useRouter, useRoute 等)
- Pinia (defineStore, storeToRefs 等)

**自动导入的组件**:
- Element Plus 组件
- 项目内自定义组件

## 🏃‍♂️ 启动和运行

### 1. 开发模式启动

```bash
# 启动开发服务器
npm run dev

# 或使用 yarn
yarn dev
```

启动成功后，控制台会显示：
```
  VITE v4.5.3  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
  ➜  press h to show help
```

### 2. 开发服务器功能

- **热模块替换 (HMR)**: 代码修改后自动更新页面
- **快速刷新**: Vue 组件状态保持
- **错误覆盖**: 编译错误直接显示在浏览器中
- **自动打开浏览器**: 启动后自动打开默认浏览器

### 3. 开发模式特性

- **Source Map**: 便于调试的源码映射
- **详细错误信息**: 完整的错误堆栈信息
- **开发工具支持**: Vue DevTools 支持
- **API 代理**: 自动代理 `/api` 请求到后端服务

## 🔨 构建和部署

### 1. 生产构建

```bash
# 构建生产版本
npm run build

# 构建完成后预览
npm run preview
```

### 2. 构建输出

构建完成后，会在 `dist/` 目录生成以下文件：
```
dist/
├── index.html              # 主 HTML 文件
├── assets/
│   ├── index-[hash].js     # 主 JavaScript 文件
│   ├── index-[hash].css    # 主 CSS 文件
│   ├── element-plus-[hash].js  # Element Plus 库
│   ├── vue-vendor-[hash].js    # Vue 相关库
│   └── utils-[hash].js     # 工具库
└── vite.svg               # 静态资源
```

### 3. 部署配置

**Nginx 配置示例**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    # 处理 Vue Router 的 history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Docker 部署**:
```dockerfile
# 构建阶段
FROM node:16-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🛠️ 开发工具配置

### 1. VS Code 配置

**推荐扩展**:
```json
{
  "recommendations": [
    "vue.volar",                    // Vue 3 语言支持
    "vue.vscode-typescript-vue-plugin",  // TypeScript 支持
    "bradlc.vscode-tailwindcss",    // Tailwind CSS 支持
    "esbenp.prettier-vscode",       // 代码格式化
    "dbaeumer.vscode-eslint",       // ESLint 支持
    "ms-vscode.vscode-json",        // JSON 支持
    "formulahendry.auto-rename-tag" // 自动重命名标签
  ]
}
```

**工作区配置** (`.vscode/settings.json`):
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "files.associations": {
    "*.vue": "vue"
  },
  "emmet.includeLanguages": {
    "vue-html": "html"
  },
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

### 2. ESLint 配置

项目使用 ESLint 进行代码检查：

```bash
# 运行 ESLint 检查
npm run lint

# 自动修复可修复的问题
npm run lint -- --fix
```

### 3. Prettier 配置

代码格式化配置 (`.prettierrc`):
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "none",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

## 🐛 常见问题解决

### 1. 依赖安装问题

**问题**: `npm install` 失败
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

**问题**: 网络超时
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 或临时使用
npm install --registry=https://registry.npmmirror.com
```

### 2. 启动问题

**问题**: 端口被占用
```bash
# 查找占用端口的进程
lsof -ti:3000

# 杀死进程
kill -9 <PID>

# 或使用不同端口启动
npm run dev -- --port 3001
```

**问题**: 代理不工作
- 检查后端服务是否启动 (localhost:8000)
- 确认 `vite.config.js` 中的代理配置
- 查看浏览器网络面板的请求状态

### 3. 构建问题

**问题**: 内存不足
```bash
# 增加 Node.js 内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

**问题**: 路径问题
- 检查 `vite.config.js` 中的 `base` 配置
- 确认静态资源路径是否正确

### 4. 开发体验问题

**问题**: HMR 不工作
- 检查文件保存是否成功
- 确认浏览器控制台是否有错误
- 重启开发服务器

**问题**: 自动导入不工作
- 检查 `auto-imports.d.ts` 文件是否存在
- 重启 TypeScript 服务 (VS Code: Ctrl+Shift+P → "TypeScript: Restart TS Server")

## 📝 开发规范

### 1. 代码提交规范

使用 Conventional Commits 规范：
```bash
# 功能开发
git commit -m "feat: 添加用户管理页面"

# 问题修复
git commit -m "fix: 修复登录页面样式问题"

# 文档更新
git commit -m "docs: 更新开发指南"

# 样式调整
git commit -m "style: 调整按钮间距"

# 重构代码
git commit -m "refactor: 重构API调用逻辑"
```

### 2. 分支管理

```bash
# 主分支
main/master     # 生产环境代码

# 开发分支
develop         # 开发环境代码

# 功能分支
feature/xxx     # 新功能开发

# 修复分支
hotfix/xxx      # 紧急修复

# 发布分支
release/xxx     # 版本发布
```

### 3. 代码审查

提交 Pull Request 前的检查清单：
- [ ] 代码通过 ESLint 检查
- [ ] 代码格式符合 Prettier 规范
- [ ] 新功能有对应的测试
- [ ] 文档已更新
- [ ] 构建成功
- [ ] 功能测试通过

### 4. 性能优化建议

- 使用 `v-show` 代替频繁切换的 `v-if`
- 合理使用 `computed` 和 `watch`
- 避免在模板中使用复杂表达式
- 使用 `key` 属性优化列表渲染
- 懒加载路由和组件
- 优化图片和静态资源

## 🔗 相关链接

- [Vue 3 官方文档](https://vuejs.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 状态管理](https://pinia.vuejs.org/)
- [Vue Router 路由](https://router.vuejs.org/)

---

*本指南将随着项目发展持续更新，如有问题请及时反馈。*