<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">
          <el-icon><Setting /></el-icon>
          <span>AI自动化测试平台</span>
        </div>
        <h2>欢迎登录</h2>
        <p>智能化接口测试与流程编排平台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="loginForm.remember">
              记住密码
            </el-checkbox>
            <el-link type="primary">
              忘记密码？
            </el-link>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>
          还没有账号？<el-link type="primary">
            立即注册
          </el-link>
        </p>
      </div>
    </div>
    
    <div class="login-bg">
      <div class="bg-content">
        <h3>AI驱动的自动化测试</h3>
        <ul>
          <li>智能参数增强</li>
          <li>可视化工作流编排</li>
          <li>一站式接口管理</li>
          <li>实时监控与分析</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    // 模拟登录API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 模拟登录成功
    if (loginForm.username === 'admin' && loginForm.password === '123456') {
      // 设置用户信息
      appStore.setUser({
        id: 1,
        username: loginForm.username,
        name: '管理员',
        avatar: '',
        roles: ['admin']
      })
      
      ElMessage.success('登录成功')
      
      // 跳转到首页
      router.push('/')
    } else {
      ElMessage.error('用户名或密码错误')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  flex: 1;
  max-width: 480px;
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px 40px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 20px;
}

.logo .el-icon {
  font-size: 32px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.login-header p {
  color: var(--text-color-regular);
  margin: 0;
}

.login-form {
  margin-bottom: 20px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  color: var(--text-color-regular);
}

.login-bg {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: white;
  position: relative;
  overflow: hidden;
}

.login-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.bg-content {
  position: relative;
  z-index: 1;
  max-width: 400px;
}

.bg-content h3 {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 30px 0;
  line-height: 1.2;
}

.bg-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.bg-content li {
  font-size: 18px;
  margin-bottom: 16px;
  padding-left: 24px;
  position: relative;
}

.bg-content li::before {
  content: '✓';
  position: absolute;
  left: 0;
  top: 0;
  color: #4ade80;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-box {
    max-width: none;
    padding: 40px 20px;
  }
  
  .login-bg {
    min-height: 300px;
    padding: 40px 20px;
  }
  
  .bg-content h3 {
    font-size: 24px;
  }
  
  .bg-content li {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .login-box {
    padding: 30px 16px;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
  
  .logo {
    font-size: 18px;
  }
  
  .logo .el-icon {
    font-size: 28px;
  }
}
</style>