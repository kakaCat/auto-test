<template>
  <el-form
    ref="formRef"
    :model="localFormData"
    :rules="rules"
    label-width="100px"
  >
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="API名称" prop="name">
          <el-input v-model="localFormData.name" placeholder="请输入API名称" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="版本" prop="version">
          <el-input v-model="localFormData.version" placeholder="如: 1.0.0" />
        </el-form-item>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="服务名称" prop="serviceName">
          <el-input v-model="localFormData.serviceName" placeholder="请输入服务名称" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="服务模块" prop="moduleId">
          <el-select v-model="localFormData.moduleId" placeholder="请选择服务模块" style="width: 100%">
            <el-option 
              v-for="module in availableModules" 
              :key="module.id" 
              :label="module.name" 
              :value="module.id" 
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="localFormData.method" placeholder="请选择请求方法">
            <el-option 
              v-for="method in httpMethods" 
              :key="method.value" 
              :label="method.label" 
              :value="method.value" 
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="通信协议" prop="protocol">
          <el-select v-model="localFormData.protocol" placeholder="请选择协议">
            <el-option 
              v-for="protocol in protocolOptions" 
              :key="protocol.value" 
              :label="protocol.label" 
              :value="protocol.value" 
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="URL" prop="url">
          <el-input v-model="localFormData.url" placeholder="api.example.com/users" />
        </el-form-item>
      </el-col>
    </el-row>
    
    <el-form-item label="描述" prop="description">
      <el-input
        v-model="localFormData.description"
        type="textarea"
        :rows="3"
        placeholder="请输入API描述"
      />
    </el-form-item>
    
    <el-form-item label="请求头">
      <div class="params-section">
        <div
          v-for="(header, index) in localFormData.headers"
          :key="index"
          class="param-row"
        >
          <el-input
            v-model="header.key"
            placeholder="Header名称"
            style="width: 200px"
          />
          <el-input
            v-model="header.value"
            placeholder="Header值"
            style="width: 300px"
          />
          <el-button
            type="text"
            @click="removeHeader(index)"
            style="color: var(--danger-color)"
          >
            删除
          </el-button>
        </div>
        <el-button type="text" @click="addHeader">
          <el-icon><Plus /></el-icon>
          添加请求头
        </el-button>
      </div>
    </el-form-item>
    
    <el-form-item label="请求参数">
      <div class="params-section">
        <div
          v-for="(param, index) in localFormData.parameters"
          :key="index"
          class="param-row"
        >
          <el-input
            v-model="param.name"
            placeholder="参数名"
            style="width: 150px"
          />
          <el-select
            v-model="param.type"
            placeholder="类型"
            style="width: 100px"
          >
            <el-option 
              v-for="type in parameterTypes" 
              :key="type.value" 
              :label="type.label" 
              :value="type.value" 
            />
          </el-select>
          <el-checkbox v-model="param.required">必填</el-checkbox>
          <el-input
            v-model="param.description"
            placeholder="参数描述"
            style="width: 200px"
          />
          <el-button
            type="text"
            @click="removeParameter(index)"
            style="color: var(--danger-color)"
          >
            删除
          </el-button>
        </div>
        <el-button type="text" @click="addParameter">
          <el-icon><Plus /></el-icon>
          添加参数
        </el-button>
      </div>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { httpMethods, protocolOptions, formRules as rules, defaultFormData, parameterTypes } from '../data'

const props = defineProps({
  formData: {
    type: Object,
    required: true
  },
  availableModules: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:form-data'])

const formRef = ref()

// 本地表单数据，用于双向绑定
const localFormData = computed({
  get: () => props.formData,
  set: (value) => emit('update:form-data', value)
})

// 监听表单数据变化，同步到父组件
watch(localFormData, (newValue) => {
  emit('update:form-data', newValue)
}, { deep: true })

// 添加请求头
const addHeader = () => {
  if (!localFormData.value.headers) {
    localFormData.value.headers = []
  }
  localFormData.value.headers.push({ key: '', value: '' })
}

// 删除请求头
const removeHeader = (index) => {
  localFormData.value.headers.splice(index, 1)
}

// 添加参数
const addParameter = () => {
  if (!localFormData.value.parameters) {
    localFormData.value.parameters = []
  }
  localFormData.value.parameters.push({
    name: '',
    type: 'string',
    required: false,
    description: ''
  })
}

// 删除参数
const removeParameter = (index) => {
  localFormData.value.parameters.splice(index, 1)
}

// 表单验证
const validate = () => {
  return formRef.value?.validate()
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  // 重置为默认数据
  Object.assign(localFormData.value, { ...defaultFormData })
}

// 暴露方法给父组件
defineExpose({
  validate,
  resetForm
})
</script>

<style scoped>
.params-section {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  background-color: var(--bg-color-light);
}

.param-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.param-row:last-child {
  margin-bottom: 0;
}
</style>