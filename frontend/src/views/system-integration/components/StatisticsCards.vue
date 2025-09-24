<template>
  <div class="statistics-cards">
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6" v-for="stat in statistics" :key="stat.title">
        <div class="stat-card" :class="`stat-card--${stat.color}`">
          <div class="stat-icon">
            <el-icon :size="24">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import {
  Connection,
  VideoPlay,
  Warning,
  DataAnalysis
} from '@element-plus/icons-vue'

interface Statistic {
  title: string
  value: number
  icon: string
  color: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

interface Props {
  statistics: Statistic[]
}

defineProps<Props>()
</script>

<style scoped>
.statistics-cards {
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  height: 100px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-card--primary .stat-icon {
  background: linear-gradient(135deg, #409eff, #337ecc);
}

.stat-card--success .stat-icon {
  background: linear-gradient(135deg, #67c23a, #529b2e);
}

.stat-card--warning .stat-icon {
  background: linear-gradient(135deg, #e6a23c, #b88230);
}

.stat-card--danger .stat-icon {
  background: linear-gradient(135deg, #f56c6c, #c45656);
}

.stat-card--info .stat-icon {
  background: linear-gradient(135deg, #909399, #73767a);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-title {
  font-size: 14px;
  color: #606266;
  line-height: 1;
}

@media (max-width: 768px) {
  .stat-card {
    padding: 16px;
    height: 80px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-title {
    font-size: 12px;
  }
}
</style>