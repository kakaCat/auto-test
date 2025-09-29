<template>
  <el-drawer
    v-model="visible"
    title="Mock数据生成器"
    size="60%"
    direction="rtl"
    :before-close="handleClose"
  >
    <div class="mock-generator">
      <!-- API信息展示 -->
      <div class="api-info">
        <h3>API信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="API名称">{{ apiInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="请求方法">
            <el-tag :type="getMethodType(apiInfo.method)">{{ apiInfo.method }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="请求URL">{{ apiInfo.url }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ apiInfo.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Mock配置 -->
      <div class="mock-config">
        <h3>Mock配置</h3>
        <el-form :model="mockConfig" label-width="120px">
          <el-form-item label="数据类型">
            <el-select v-model="mockConfig.dataType" placeholder="选择数据类型">
              <el-option label="JSON对象" value="object" />
              <el-option label="JSON数组" value="array" />
              <el-option label="字符串" value="string" />
              <el-option label="数字" value="number" />
              <el-option label="布尔值" value="boolean" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="数据条数" v-if="mockConfig.dataType === 'array'">
            <el-input-number v-model="mockConfig.arraySize" :min="1" :max="100" />
          </el-form-item>

          <el-form-item label="字段配置" v-if="['object', 'array'].includes(mockConfig.dataType)">
            <div class="field-config">
              <div v-for="(field, index) in mockConfig.fields" :key="index" class="field-item">
                <el-input
                  v-model="field.name"
                  placeholder="字段名"
                  style="width: 150px; margin-right: 10px;"
                />
                <el-select
                  v-model="field.type"
                  placeholder="字段类型"
                  style="width: 120px; margin-right: 10px;"
                >
                  <el-option label="字符串" value="string" />
                  <el-option label="数字" value="number" />
                  <el-option label="布尔值" value="boolean" />
                  <el-option label="日期" value="date" />
                  <el-option label="邮箱" value="email" />
                  <el-option label="手机号" value="phone" />
                  <el-option label="URL" value="url" />
                  <el-option label="UUID" value="uuid" />
                </el-select>
                <el-input
                  v-model="field.description"
                  placeholder="字段描述"
                  style="width: 150px; margin-right: 10px;"
                />
                <el-button
                  type="danger"
                  size="small"
                  @click="removeField(index)"
                  :disabled="mockConfig.fields.length <= 1"
                >
                  删除
                </el-button>
              </div>
              <el-button type="primary" size="small" @click="addField">添加字段</el-button>
            </div>
          </el-form-item>

          <el-form-item label="智能推荐">
            <el-button type="success" @click="generateSmartFields">
              <el-icon><Star /></el-icon>
              根据API自动推荐字段
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Mock数据预览 -->
      <div class="mock-preview">
        <h3>
          Mock数据预览
          <el-button type="primary" size="small" @click="generateMockData" style="margin-left: 10px;">
            <el-icon><Refresh /></el-icon>
            重新生成
          </el-button>
        </h3>
        <el-input
          v-model="generatedMockData"
          type="textarea"
          :rows="15"
          readonly
          placeholder="点击生成按钮查看Mock数据"
        />
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="copyMockData" :disabled="!generatedMockData">
          <el-icon><DocumentCopy /></el-icon>
          复制数据
        </el-button>
        <el-button type="success" @click="saveMockConfig">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, Refresh, DocumentCopy, Check } from '@element-plus/icons-vue'
import { apiManagementApi } from '@/api/api-management'
import type { MockConfig, MockFieldConfig } from '@/api/api-management'
import type { ApiItem } from '../data/tableColumns'

// Props
interface Props {
  modelValue: boolean
  apiInfo: ApiItem
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'mock-generated': [data: any]
}>()

// 响应式数据
const visible = ref(props.modelValue)
const generatedMockData = ref('')

// Mock配置
const mockConfig = reactive<MockConfig>({
  dataType: 'object',
  arraySize: 5,
  fields: [
    { name: 'id', type: 'number', description: '唯一标识' },
    { name: 'name', type: 'string', description: '名称' }
  ]
})

// 监听visible变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    generateMockData()
  }
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 获取方法类型样式
const getMethodType = (method: string): string => {
  const typeMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return typeMap[method] || 'info'
}

// 添加字段
const addField = () => {
  mockConfig.fields.push({
    name: '',
    type: 'string',
    description: ''
  })
}

// 删除字段
const removeField = (index: number) => {
  if (mockConfig.fields.length > 1) {
    mockConfig.fields.splice(index, 1)
  }
}

// 智能推荐字段
const generateSmartFields = async () => {
  try {
    // 首先尝试从API获取智能推荐
    const response = await apiManagementApi.getSmartFieldRecommendations(props.apiInfo.id.toString())
    if (response.success && response.data) {
      mockConfig.fields = response.data
      ElMessage.success('已获取API智能推荐字段')
      generateMockData()
      return
    }
  } catch (error) {
    console.warn('API智能推荐失败，使用本地推荐逻辑:', error)
  }

  // 如果API调用失败，使用本地推荐逻辑
  const apiName = props.apiInfo.name.toLowerCase()
  const url = props.apiInfo.url.toLowerCase()
  
  // 根据API名称和URL智能推荐字段
  const smartFields: MockFieldConfig[] = []
  
  if (apiName.includes('user') || url.includes('user')) {
    smartFields.push(
      { name: 'id', type: 'number', description: '用户ID' },
      { name: 'username', type: 'string', description: '用户名' },
      { name: 'email', type: 'email', description: '邮箱' },
      { name: 'phone', type: 'phone', description: '手机号' },
      { name: 'createTime', type: 'date', description: '创建时间' }
    )
  } else if (apiName.includes('order') || url.includes('order')) {
    smartFields.push(
      { name: 'orderId', type: 'string', description: '订单号' },
      { name: 'amount', type: 'number', description: '金额' },
      { name: 'status', type: 'string', description: '订单状态' },
      { name: 'createTime', type: 'date', description: '创建时间' }
    )
  } else if (apiName.includes('product') || url.includes('product')) {
    smartFields.push(
      { name: 'productId', type: 'string', description: '产品ID' },
      { name: 'productName', type: 'string', description: '产品名称' },
      { name: 'price', type: 'number', description: '价格' },
      { name: 'category', type: 'string', description: '分类' }
    )
  } else {
    smartFields.push(
      { name: 'id', type: 'uuid', description: '唯一标识' },
      { name: 'name', type: 'string', description: '名称' },
      { name: 'status', type: 'string', description: '状态' },
      { name: 'createTime', type: 'date', description: '创建时间' }
    )
  }
  
  mockConfig.fields = smartFields
  ElMessage.success('已根据API智能推荐字段')
  generateMockData()
}

// 生成Mock数据
const generateMockData = () => {
  try {
    let mockData: any
    
    if (mockConfig.dataType === 'object') {
      mockData = generateObject()
    } else if (mockConfig.dataType === 'array') {
      mockData = Array.from({ length: mockConfig.arraySize }, () => generateObject())
    } else {
      mockData = generatePrimitiveValue(mockConfig.dataType)
    }
    
    generatedMockData.value = JSON.stringify(mockData, null, 2)
  } catch (error) {
    ElMessage.error('生成Mock数据失败')
    console.error(error)
  }
}

// 生成对象
const generateObject = () => {
  const obj: any = {}
  mockConfig.fields.forEach(field => {
    if (field.name) {
      obj[field.name] = generateFieldValue(field.type)
    }
  })
  return obj
}

// 生成字段值
const generateFieldValue = (type: string): any => {
  switch (type) {
    case 'string':
      return `示例${Math.random().toString(36).substr(2, 8)}`
    case 'number':
      return Math.floor(Math.random() * 1000) + 1
    case 'boolean':
      return Math.random() > 0.5
    case 'date':
      return new Date().toISOString()
    case 'email':
      return `user${Math.floor(Math.random() * 1000)}@example.com`
    case 'phone':
      return `1${Math.floor(Math.random() * 9000000000) + 1000000000}`
    case 'url':
      return `https://example.com/path/${Math.random().toString(36).substr(2, 8)}`
    case 'uuid':
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    default:
      return null
  }
}

// 生成基础类型值
const generatePrimitiveValue = (type: string): any => {
  return generateFieldValue(type)
}

// 复制Mock数据
const copyMockData = async () => {
  try {
    await navigator.clipboard.writeText(generatedMockData.value)
    ElMessage.success('Mock数据已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 保存Mock配置
const saveMockConfig = async () => {
  try {
    // 生成Mock数据
    const generateResponse = await apiManagementApi.generateMockData({
      apiId: props.apiInfo.id.toString(),
      config: mockConfig
    })
    
    if (generateResponse.success) {
      // 保存Mock配置
      await apiManagementApi.saveMockConfig(props.apiInfo.id.toString(), mockConfig)
      
      ElMessage.success('Mock配置已保存并生成数据')
      emit('mock-generated', {
        apiId: props.apiInfo.id,
        config: mockConfig,
        data: generateResponse.data?.mockData || generatedMockData.value
      })
    } else {
      ElMessage.error('生成Mock数据失败')
    }
  } catch (error) {
    console.error('保存Mock配置失败:', error)
    ElMessage.error('保存Mock配置失败')
    // 如果API调用失败，仍然发送本地生成的数据
    emit('mock-generated', {
      apiId: props.apiInfo.id,
      config: mockConfig,
      data: generatedMockData.value
    })
  }
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.mock-generator {
  padding: 20px;
}

.api-info,
.mock-config,
.mock-preview {
  margin-bottom: 30px;
}

.api-info h3,
.mock-config h3,
.mock-preview h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.field-config {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.field-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.field-item:last-child {
  margin-bottom: 0;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-drawer__header) {
  margin-bottom: 20px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>