<template>
  <div class="api-test">
    <el-card>
      <template #header>
        <h2>API功能测试</h2>
      </template>
      
      <div class="test-section">
        <h3>当前API状态</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="API类型">
            {{ apiStatus.currentApi }}
          </el-descriptions-item>
          <el-descriptions-item label="API健康状态">
            <el-tag :type="apiStatus.apiHealth.unified ? 'success' : 'danger'">
              {{ apiStatus.apiHealth.unified ? '正常' : '异常' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="test-section">
        <h3>API调用测试</h3>
        <el-space>
          <el-button type="success" @click="testApiCall" :loading="testing">
            测试API调用
          </el-button>
        </el-space>
        
        <div v-if="testResult" class="test-result">
          <h4>测试结果:</h4>
          <el-alert 
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.message"
            show-icon
          />
          <pre v-if="testResult.data">{{ JSON.stringify(testResult.data, null, 2) }}</pre>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiManagementApi } from '@/api/unified-api'

// 响应式数据
const apiStatus = ref({
  currentApi: 'unified',
  apiHealth: {
    unified: true
  }
})

const testing = ref(false)
const testResult = ref(null)

// 测试API调用
const testApiCall = async () => {
  testing.value = true
  testResult.value = null
  
  try {
    // 直接使用统一API测试获取统计数据
    if (apiManagementApi && apiManagementApi.getStats) {
      const response = await apiManagementApi.getStats()
      testResult.value = {
        success: true,
        message: 'API调用成功',
        data: response
      }
    } else {
      testResult.value = {
        success: false,
        message: 'API方法不可用'
      }
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: 'API调用失败: ' + error.message
    }
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
}

.test-section {
  margin-bottom: 30px;
}

.test-section h3 {
  margin-bottom: 15px;
  color: #409eff;
}

.test-result {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.test-result pre {
  margin-top: 10px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}
</style>