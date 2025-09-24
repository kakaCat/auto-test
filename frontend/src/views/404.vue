<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-illustration">
        <div class="error-number">404</div>
        <div class="error-icon">
          <el-icon><DocumentDelete /></el-icon>
        </div>
      </div>
      
      <div class="error-info">
        <h1>页面未找到</h1>
        <p>抱歉，您访问的页面不存在或已被移除</p>
        
        <div class="error-suggestions">
          <h3>您可以尝试：</h3>
          <ul>
            <li>检查网址是否正确</li>
            <li>返回上一页继续浏览</li>
            <li>访问首页查看其他内容</li>
            <li>联系管理员获取帮助</li>
          </ul>
        </div>
        
        <div class="error-actions">
          <el-button type="primary" @click="goHome">
            <el-icon><House /></el-icon>
            返回首页
          </el-button>
          <el-button @click="goBack">
            <el-icon><Back /></el-icon>
            返回上页
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="error-footer">
      <p>如果问题持续存在，请联系技术支持</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  text-align: center;
}

.error-content {
  max-width: 600px;
  width: 100%;
}

.error-illustration {
  position: relative;
  margin-bottom: 40px;
}

.error-number {
  font-size: 120px;
  font-weight: 900;
  color: var(--primary-color);
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, var(--primary-color), #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.error-icon {
  font-size: 80px;
  color: var(--text-color-regular);
  opacity: 0.6;
}

.error-info h1 {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 16px 0;
}

.error-info p {
  font-size: 18px;
  color: var(--text-color-regular);
  margin: 0 0 40px 0;
  line-height: 1.6;
}

.error-suggestions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.error-suggestions h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 16px 0;
}

.error-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.error-suggestions li {
  padding: 8px 0;
  color: var(--text-color-regular);
  position: relative;
  padding-left: 24px;
}

.error-suggestions li::before {
  content: '•';
  position: absolute;
  left: 0;
  top: 8px;
  color: var(--primary-color);
  font-weight: bold;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.error-actions .el-button {
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
}

.error-footer {
  margin-top: 60px;
  color: var(--text-color-secondary);
  font-size: 14px;
}

/* 动画效果 */
.error-number {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.error-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-number {
    font-size: 80px;
  }
  
  .error-icon {
    font-size: 60px;
  }
  
  .error-info h1 {
    font-size: 24px;
  }
  
  .error-info p {
    font-size: 16px;
  }
  
  .error-suggestions {
    padding: 20px;
    text-align: center;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .el-button {
    width: 200px;
  }
}

@media (max-width: 480px) {
  .error-page {
    padding: 20px 16px;
  }
  
  .error-number {
    font-size: 60px;
  }
  
  .error-icon {
    font-size: 40px;
  }
  
  .error-info h1 {
    font-size: 20px;
  }
  
  .error-suggestions {
    padding: 16px;
  }
  
  .error-suggestions h3 {
    font-size: 16px;
  }
}
</style>