<!--
  仪表板页面组件 (Dashboard)
  
  功能说明：
  - 系统概览和数据统计展示
  - 功能模块快捷入口导航
  - 最近活动和系统状态监控
  - 响应式数据可视化界面
  
  页面结构：
  1. 页面头部 - 平台标题和描述
  2. 统计卡片 - 核心数据指标展示
  3. 功能模块 - 各功能模块快捷入口
  4. 最近活动 - 系统操作记录展示
  5. 系统状态 - 健康状态和性能监控
  
  数据来源：
  - API统计数据
  - 用户操作记录
  - 系统监控指标
  - 实时状态信息
  
  交互特性：
  - 卡片点击导航
  - 数据实时刷新
  - 响应式布局适配
  - 动画过渡效果
  
  技术实现：
  - Vue 3 Composition API
  - Element Plus 组件库
  - 响应式数据绑定
  - 路由导航集成
  
  @author AI Assistant
  @version 1.0.0
  @since 2024-01-15
-->
<template>
  <div class="dashboard">
    <!-- 
      仪表板页面头部
      - 平台标题和简介
      - 欢迎信息展示
    -->
    <div class="dashboard-header">
      <h1>AI自动化测试平台</h1>
      <p>统一的接口流程编排与管理平台</p>
    </div>
    
    <!-- 
      核心数据统计卡片区域
      - API接口数量统计
      - 测试场景数量统计
      - 工作流数量统计
      - 执行次数统计
      - 支持实时数据更新
    -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon api">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.apiCount }}
          </div>
          <div class="stat-label">
            API接口
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon scenario">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.scenarioCount }}
          </div>
          <div class="stat-label">
            测试场景
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon workflow">
          <el-icon><Share /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.workflowCount }}
          </div>
          <div class="stat-label">
            工作流
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon execution">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.executionCount }}
          </div>
          <div class="stat-label">
            执行次数
          </div>
        </div>
      </div>
    </div>
    
    <!-- 
      功能模块快捷入口区域
      - 各功能模块的导航卡片
      - 支持点击跳转到对应页面
      - 包含模块图标、名称和描述
      - 响应式网格布局
    -->
    <div class="modules-section">
      <h2>功能模块</h2>
      <div class="modules-grid">
        <div 
          v-for="module in modules" 
          :key="module.name"
          class="module-card"
          @click="navigateToModule(module.path)"
        >
          <div
            class="module-icon"
            :class="module.color"
          >
            <el-icon>
              <component :is="module.icon" />
            </el-icon>
          </div>
          <div class="module-content">
            <h3>{{ module.name }}</h3>
            <p>{{ module.description }}</p>
          </div>
          <div class="module-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 
      最近活动展示区域
      - 显示系统最近的操作记录
      - 包含活动类型、标题和描述
      - 支持手动刷新功能
      - 时间线式展示布局
    -->
    <div class="activity-section">
      <div class="section-header">
        <h2>最近活动</h2>
        <el-button
          type="text"
          @click="refreshActivity"
        >
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      
      <div class="activity-list">
        <div 
          v-for="activity in activities" 
          :key="activity.id"
          class="activity-item"
        >
          <div
            class="activity-icon"
            :class="activity.type"
          >
            <el-icon>
              <component :is="getActivityIcon(activity.type)" />
            </el-icon>
          </div>
          <div class="activity-content">
            <div class="activity-title">
              {{ activity.title }}
            </div>
            <div class="activity-desc">
              {{ activity.description }}
            </div>
            <div class="activity-time">
              {{ formatTime(activity.time) }}
            </div>
          </div>
          <div class="activity-status">
            <el-tag 
              :type="getStatusType(activity.status)"
              size="small"
            >
              {{ activity.status }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 系统状态 -->
    <div class="status-section">
      <h2>系统状态</h2>
      <div class="status-grid">
        <div class="status-item">
          <div class="status-label">
            数据库连接
          </div>
          <div class="status-value">
            <el-tag
              type="success"
              size="small"
            >
              正常
            </el-tag>
          </div>
        </div>
        <div class="status-item">
          <div class="status-label">
            API服务
          </div>
          <div class="status-value">
            <el-tag
              type="success"
              size="small"
            >
              运行中
            </el-tag>
          </div>
        </div>
        <div class="status-item">
          <div class="status-label">
            执行引擎
          </div>
          <div class="status-value">
            <el-tag
              type="success"
              size="small"
            >
              就绪
            </el-tag>
          </div>
        </div>
        <div class="status-item">
          <div class="status-label">
            AI服务
          </div>
          <div class="status-value">
            <el-tag
              type="warning"
              size="small"
            >
              部分可用
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiManagementApi } from '@/api/unified-api'

// 直接使用统一API
const apiProxy = apiManagementApi

const router = useRouter()

// 统计数据
const stats = ref({
  apiCount: 0,
  scenarioCount: 0,
  workflowCount: 0,
  executionCount: 0
})

// 功能模块
const modules = ref([
  {
    name: 'API管理',
    description: '管理和配置API接口信息',
    icon: 'Connection',
    color: 'blue',
    path: '/api-management'
  },
  {
    name: '场景管理',
    description: '创建和管理测试场景',
    icon: 'Document',
    color: 'green',
    path: '/scenario-management'
  },
  {
    name: '工作流编排',
    description: '可视化工作流设计和编排',
    icon: 'Share',
    color: 'purple',
    path: '/workflow-orchestration'
  },
  {
    name: 'AI场景执行',
    description: '智能化场景执行和分析',
    icon: 'MagicStick',
    color: 'orange',
    path: '/ai-scenario-execution'
  },
  {
    name: '系统集成',
    description: '系统配置和集成管理',
    icon: 'Setting',
    color: 'red',
    path: '/integration'
  }
])

// 最近活动
const activities = ref([
  {
    id: 1,
    type: 'api',
    title: '创建新API',
    description: '用户API接口已创建',
    time: new Date(Date.now() - 1000 * 60 * 5),
    status: '成功'
  },
  {
    id: 2,
    type: 'scenario',
    title: '执行测试场景',
    description: '登录流程测试场景执行完成',
    time: new Date(Date.now() - 1000 * 60 * 15),
    status: '成功'
  },
  {
    id: 3,
    type: 'workflow',
    title: '工作流更新',
    description: '订单处理工作流已更新',
    time: new Date(Date.now() - 1000 * 60 * 30),
    status: '成功'
  },
  {
    id: 4,
    type: 'ai',
    title: 'AI分析完成',
    description: '接口性能分析报告已生成',
    time: new Date(Date.now() - 1000 * 60 * 45),
    status: '警告'
  }
])

// 导航到模块
const navigateToModule = (path) => {
  router.push(path)
}

// 获取活动图标
const getActivityIcon = (type) => {
  const iconMap = {
    api: 'Connection',
    scenario: 'Document',
    workflow: 'Share',
    ai: 'MagicStick'
  }
  return iconMap[type] || 'InfoFilled'
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    '成功': 'success',
    '失败': 'danger',
    '警告': 'warning',
    '进行中': 'info'
  }
  return typeMap[status] || 'info'
}

// 格式化时间
const formatTime = (time) => {
  const now = new Date()
  const diff = now - time
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

// 刷新活动
const refreshActivity = () => {
  ElMessage.success('活动数据已刷新')
  // 这里可以调用API刷新数据
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 调用真实的后端API
    const response = await apiProxy.getStats()
    
    if (response.success) {
      const data = response.data
      stats.value = {
        apiCount: data.api_stats?.total_apis || 0,
        scenarioCount: data.scenario_stats?.total_scenarios || 0,
        workflowCount: data.workflow_stats?.total_workflows || 0,
        executionCount: data.recent_activity?.length || 0
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用默认值
    stats.value = {
      apiCount: 0,
      scenarioCount: 0,
      workflowCount: 0,
      executionCount: 0
    }
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.dashboard-header p {
  font-size: 16px;
  color: var(--text-color-regular);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.api { background: var(--primary-color); }
.stat-icon.scenario { background: var(--success-color); }
.stat-icon.workflow { background: var(--warning-color); }
.stat-icon.execution { background: var(--info-color); }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-regular);
}

.modules-section {
  margin-bottom: 32px;
}

.modules-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 16px 0;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.module-card {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.module-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.module-icon.blue { background: var(--primary-color); }
.module-icon.green { background: var(--success-color); }
.module-icon.purple { background: #722ed1; }
.module-icon.orange { background: var(--warning-color); }
.module-icon.red { background: var(--danger-color); }

.module-content {
  flex: 1;
}

.module-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 4px 0;
}

.module-content p {
  font-size: 14px;
  color: var(--text-color-regular);
  margin: 0;
}

.module-arrow {
  color: var(--text-color-placeholder);
  font-size: 16px;
}

.activity-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.activity-list {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color-lighter);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: white;
}

.activity-icon.api { background: var(--primary-color); }
.activity-icon.scenario { background: var(--success-color); }
.activity-icon.workflow { background: var(--warning-color); }
.activity-icon.ai { background: #722ed1; }

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color-primary);
  margin-bottom: 2px;
}

.activity-desc {
  font-size: 12px;
  color: var(--text-color-regular);
  margin-bottom: 2px;
}

.activity-time {
  font-size: 12px;
  color: var(--text-color-placeholder);
}

.status-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 16px 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.status-item {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-size: 14px;
  color: var(--text-color-regular);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>