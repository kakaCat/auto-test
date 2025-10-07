<template>
  <div
    class="demo-wrapper"
    role="region"
    aria-label="ParamsEditor 完整功能演示"
  >
    <header class="demo-header">
      <h2>ParamsEditor 完整功能演示</h2>
      <p>
        演示：参数编辑器的完整功能，包括折叠状态持久化、键盘导航、A11y属性、JSON导入等核心特性。
      </p>
    </header>

    <!-- 功能选项卡 -->
    <section class="demo-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-button', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </section>

    <!-- 基础配置控制 -->
    <section
      v-show="activeTab === 'basic'"
      class="controls"
      aria-label="基础配置"
    >
      <h3>基础配置</h3>
      <div class="control-group">
        <label>
          默认展开层级：
          <input
            v-model.number="defaultExpandDepth"
            type="number"
            min="0"
            max="6"
          >
        </label>
        <label>
          最大自动展开节点数：
          <input
            v-model.number="maxAutoExpandNodes"
            type="number"
            min="10"
            max="1000"
          >
        </label>
        <label>
          组件ID（命名空间）：
          <input
            v-model="componentId"
            type="text"
          >
        </label>
      </div>
      <div class="control-actions">
        <button @click="resetLocalStorage">
          清除持久化折叠状态
        </button>
        <button
          :disabled="isLoadingLargeDataset"
          @click="loadLargeDataset"
        >
          {{ isLoadingLargeDataset ? '加载中...' : '加载大型数据集 (2k+ 节点)' }}
        </button>
        <button @click="loadSmallDataset">
          恢复小型数据集
        </button>
      </div>
    </section>

    <!-- JSON导入演示 -->
    <section
      v-show="activeTab === 'json-import'"
      class="json-import-demo"
      aria-label="JSON导入演示"
    >
      <h3>JSON 导入功能演示</h3>
      <div class="demo-examples">
        <div class="example-buttons">
          <button 
            v-for="example in jsonExamples" 
            :key="example.name"
            class="example-btn"
            @click="loadJsonExample(example)"
          >
            {{ example.name }}
          </button>
          <button
            class="import-btn"
            @click="showJsonImportModal = true"
          >
            自定义 JSON 导入
          </button>
        </div>
        <div
          v-if="currentExample"
          class="example-description"
        >
          <h4>{{ currentExample.name }}</h4>
          <p>{{ currentExample.description }}</p>
          <details class="example-json">
            <summary>查看 JSON 数据</summary>
            <pre><code>{{ JSON.stringify(currentExample.data, null, 2) }}</code></pre>
          </details>
        </div>
      </div>
    </section>

    <!-- 性能测试 -->
    <section
      v-show="activeTab === 'performance'"
      class="performance-demo"
      aria-label="性能测试"
    >
      <h3>性能测试</h3>
      <div class="performance-controls">
        <button
          :disabled="isRunningTest"
          @click="runPerformanceTest"
        >
          {{ isRunningTest ? '测试中...' : '运行性能测试' }}
        </button>
        <button @click="clearPerformanceResults">
          清除结果
        </button>
      </div>
      <div
        v-if="performanceResults.length > 0"
        class="performance-results"
      >
        <h4>测试结果</h4>
        <div
          v-for="result in performanceResults"
          :key="result.id"
          class="result-item"
        >
          <strong>{{ result.name }}</strong>
          <span>节点数: {{ result.nodeCount }}</span>
          <span>处理时间: {{ result.processingTime }}ms</span>
          <span>渲染时间: {{ result.renderTime }}ms</span>
        </div>
      </div>
    </section>

    <!-- 参数编辑器 -->
    <section class="editor-section">
      <div class="editor-header">
        <h3>参数编辑器</h3>
        <div class="editor-stats">
          <span>参数数量: {{ params.length }}</span>
          <span>节点总数: {{ totalNodeCount }}</span>
        </div>
      </div>
      <ParamsEditor
        v-model="params"
        :collapsible="true"
        :default-expand-depth="defaultExpandDepth"
        :persist-expand-state="true"
        :max-auto-expand-nodes="maxAutoExpandNodes"
        :component-id="componentId"
        style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px;"
        @expand-change="onExpandChange"
      />
    </section>

    <!-- JSON 导入模态框 -->
    <JsonImportModal
      v-model:visible="showJsonImportModal"
      :current-params="params"
      @import="handleJsonImport"
      @close="showJsonImportModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ParamsEditor from '@/components/common/ParamsEditor.vue'
import JsonImportModal from '@/components/common/JsonImportModal.vue'

// 基础配置
const defaultExpandDepth = ref(2)
const maxAutoExpandNodes = ref(200)
const componentId = ref('demo-params-editor')
const isLoadingLargeDataset = ref(false)

// 选项卡管理
const activeTab = ref('basic')
const tabs = [
  { key: 'basic', label: '基础配置' },
  { key: 'json-import', label: 'JSON 导入' },
  { key: 'performance', label: '性能测试' }
]

// JSON 导入相关
const showJsonImportModal = ref(false)
const currentExample = ref(null)

// 性能测试相关
const isRunningTest = ref(false)
const performanceResults = ref([])

// JSON 示例数据
const jsonExamples = [
  {
    name: '用户信息',
    description: '典型的用户信息结构，包含基本信息和嵌套对象',
    data: {
      id: 12345,
      username: 'john_doe',
      email: 'john@example.com',
      profile: {
        firstName: 'John',
        lastName: 'Doe',
        age: 30,
        avatar: 'https://example.com/avatar.jpg',
        preferences: {
          theme: 'dark',
          language: 'zh-CN',
          notifications: true
        }
      },
      roles: ['user', 'admin'],
      lastLogin: '2024-01-15T10:30:00Z',
      isActive: true
    }
  },
  {
    name: 'API 响应',
    description: '典型的 API 响应结构，包含分页和数据列表',
    data: {
      code: 200,
      message: 'success',
      data: {
        list: [
          {
            id: 1,
            title: '测试项目',
            status: 'active',
            createdAt: '2024-01-15T10:00:00Z'
          },
          {
            id: 2,
            title: '演示项目',
            status: 'pending',
            createdAt: '2024-01-15T11:00:00Z'
          }
        ],
        pagination: {
          page: 1,
          size: 20,
          total: 100,
          totalPages: 5
        }
      },
      timestamp: 1705312200000
    }
  },
  {
    name: '复杂嵌套',
    description: '深层嵌套结构，测试多级展开和性能',
    data: {
      level1: {
        level2: {
          level3: {
            level4: {
              level5: {
                data: 'deep nested value',
                array: [
                  { item: 1, nested: { value: 'a' } },
                  { item: 2, nested: { value: 'b' } },
                  { item: 3, nested: { value: 'c' } }
                ]
              }
            }
          }
        }
      },
      metadata: {
        version: '1.0.0',
        author: 'system',
        tags: ['test', 'demo', 'nested']
      }
    }
  },
  {
    name: '数组示例',
    description: '各种数组类型的示例，测试数组处理能力',
    data: {
      simpleArray: [1, 2, 3, 4, 5],
      stringArray: ['apple', 'banana', 'cherry'],
      objectArray: [
        { name: 'Alice', age: 25 },
        { name: 'Bob', age: 30 },
        { name: 'Charlie', age: 35 }
      ],
      mixedArray: [
        'string',
        123,
        true,
        { key: 'value' },
        [1, 2, 3]
      ],
      nestedArrays: [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
      ]
    }
  }
]

// 示例参数模型（简化），覆盖数组、对象和基本类型
const smallDataset = [
  { name: 'user', type: 'object', children: [
    { name: 'id', type: 'number', value: 123 },
    { name: 'profile', type: 'object', children: [
      { name: 'nickname', type: 'string', value: 'tester' },
      { name: 'tags', type: 'array', children: [
        { name: '0', type: 'string', value: 'alpha' },
        { name: '1', type: 'string', value: 'beta' },
        { name: '2', type: 'string', value: 'gamma' }
      ]}
    ]}
  ]},
  { name: 'meta', type: 'object', children: [
    { name: 'page', type: 'number', value: 1 },
    { name: 'size', type: 'number', value: 20 },
    { name: 'filters', type: 'array', children: [
      { name: '0', type: 'object', children: [
        { name: 'key', type: 'string', value: 'status' },
        { name: 'op', type: 'string', value: 'eq' },
        { name: 'val', type: 'string', value: 'active' }
      ]},
      { name: '1', type: 'object', children: [
        { name: 'key', type: 'string', value: 'role' },
        { name: 'op', type: 'string', value: 'in' },
        { name: 'val', type: 'array', children: [
          { name: '0', type: 'string', value: 'admin' },
          { name: '1', type: 'string', value: 'qa' }
        ]}
      ]}
    ]}
  ]}
]

const params = ref([...smallDataset])

// 计算属性
const totalNodeCount = computed(() => {
  return countNodes(params.value)
})

// 事件处理函数
function onExpandChange(payload) {
  // 仅用于演示：在控制台输出折叠变更事件
  // payload: { keyPath: string[], expanded: boolean, expandedKeys: string[] }
  // 可结合快捷键：ArrowLeft/ArrowRight/Enter 进行试用
  // eslint-disable-next-line no-console
  console.log('[expand-change]', payload)
}

// JSON 导入相关方法
function loadJsonExample(example) {
  currentExample.value = example
  const startTime = performance.now()
  
  // 转换 JSON 为参数格式
  const convertedParams = convertJsonToParams(example.data)
  params.value = convertedParams
  
  const endTime = performance.now()
  
  // eslint-disable-next-line no-console
  console.log(`🔄 加载示例 "${example.name}"`)
  // eslint-disable-next-line no-console
  console.log(`  ⏱️ 转换时间: ${(endTime - startTime).toFixed(2)}ms`)
  // eslint-disable-next-line no-console
  console.log(`  📈 节点总数: ${countNodes(convertedParams)}`)
}

function handleJsonImport(importData) {
  const startTime = performance.now()
  
  // 根据导入选项处理参数
  if (importData.options.mode === 'override') {
    params.value = importData.params
  } else {
    // 合并模式：将新参数添加到现有参数中
    params.value = [...params.value, ...importData.params]
  }
  
  const endTime = performance.now()
  
  // eslint-disable-next-line no-console
  console.log('📥 JSON 导入完成')
  // eslint-disable-next-line no-console
  console.log(`  📊 导入参数数: ${importData.params.length}`)
  // eslint-disable-next-line no-console
  console.log(`  ⏱️ 处理时间: ${(endTime - startTime).toFixed(2)}ms`)
  // eslint-disable-next-line no-console
  console.log(`  📈 当前总节点数: ${countNodes(params.value)}`)
  
  showJsonImportModal.value = false
}

// 性能测试方法
async function runPerformanceTest() {
  isRunningTest.value = true
  
  const testCases = [
    { name: '小型数据集', data: smallDataset },
    { name: '用户信息示例', data: convertJsonToParams(jsonExamples[0].data) },
    { name: 'API响应示例', data: convertJsonToParams(jsonExamples[1].data) },
    { name: '复杂嵌套示例', data: convertJsonToParams(jsonExamples[2].data) }
  ]
  
  // 如果有大型数据集，也加入测试
  if (params.value.length > 100) {
    testCases.push({ name: '当前大型数据集', data: params.value })
  }
  
  for (const testCase of testCases) {
    const startTime = performance.now()
    
    // 模拟数据处理
    const nodeCount = countNodes(testCase.data)
    
    // 模拟渲染时间（设置参数）
    const renderStart = performance.now()
    params.value = [...testCase.data]
    await new Promise(resolve => setTimeout(resolve, 10)) // 等待渲染
    const renderEnd = performance.now()
    
    const endTime = performance.now()
    
    performanceResults.value.push({
      id: Date.now() + Math.random(),
      name: testCase.name,
      nodeCount,
      processingTime: (renderStart - startTime).toFixed(2),
      renderTime: (renderEnd - renderStart).toFixed(2),
      totalTime: (endTime - startTime).toFixed(2)
    })
  }
  
  isRunningTest.value = false
}

function clearPerformanceResults() {
  performanceResults.value = []
}

function resetLocalStorage() {
  try {
    const ns = `paramsEditor:expandedKeys:${componentId.value}`
    localStorage.removeItem(ns)
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('无法清理本地存储：', e)
  }
}

// 将JSON数据转换为ParamsEditor格式
function convertJsonToParams(obj, parentName = '') {
  const result = []
  
  for (const [key, value] of Object.entries(obj)) {
    const item = { name: key }
    
    if (value === null) {
      item.type = 'string'
      item.value = null
    } else if (Array.isArray(value)) {
      item.type = 'array'
      item.children = value.map((item, index) => {
        if (typeof item === 'object' && item !== null) {
          return {
            name: index.toString(),
            type: 'object',
            children: convertJsonToParams(item)
          }
        } else {
          return {
            name: index.toString(),
            type: typeof item,
            value: item
          }
        }
      })
    } else if (typeof value === 'object') {
      item.type = 'object'
      item.children = convertJsonToParams(value)
    } else {
      item.type = typeof value
      item.value = value
    }
    
    result.push(item)
  }
  
  return result
}

async function loadLargeDataset() {
  isLoadingLargeDataset.value = true
  
  try {
    // 记录开始时间
    const startTime = performance.now()
    
    // 加载大型数据集
    const response = await fetch('/src/views/dev/large-dataset-sample.json')
    const largeData = await response.json()
    
    // 转换为ParamsEditor格式
    const convertedParams = convertJsonToParams(largeData)
    
    // 记录转换时间
    const convertTime = performance.now()
    
    // 更新参数
    params.value = convertedParams
    
    // 记录渲染时间
    const endTime = performance.now()
    
    // 输出性能指标
    // eslint-disable-next-line no-console
    console.log('🚀 大型数据集性能指标:')
    // eslint-disable-next-line no-console
    console.log(`  📊 数据加载时间: ${(convertTime - startTime).toFixed(2)}ms`)
    // eslint-disable-next-line no-console
    console.log(`  🔄 数据转换时间: ${(endTime - convertTime).toFixed(2)}ms`)
    // eslint-disable-next-line no-console
    console.log(`  ⏱️ 总处理时间: ${(endTime - startTime).toFixed(2)}ms`)
    // eslint-disable-next-line no-console
    console.log(`  📈 节点总数: ${countNodes(convertedParams)}`)
    
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('加载大型数据集失败:', error)
  } finally {
    isLoadingLargeDataset.value = false
  }
}

function loadSmallDataset() {
  const startTime = performance.now()
  params.value = [...smallDataset]
  const endTime = performance.now()
  
  // eslint-disable-next-line no-console
  console.log(`🔄 恢复小型数据集，处理时间: ${(endTime - startTime).toFixed(2)}ms`)
}

// 递归计算节点总数
function countNodes(nodes) {
  let count = 0
  for (const node of nodes) {
    count++
    if (node.children) {
      count += countNodes(node.children)
    }
  }
  return count
}
</script>

<style scoped>
.demo-wrapper {
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 12px;
  padding: 12px;
}
.demo-header h2 {
  margin: 0 0 4px;
  font-size: 18px;
}
.controls {
  display: flex;
  gap: 16px;
  align-items: center;
}
.controls label {
  display: flex;
  gap: 8px;
  align-items: center;
}
.editor-section {
  min-height: 300px;
}

/* 示例按钮样式 */
.example-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.example-btn {
  padding: 8px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #f8f9fa;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.example-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.example-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.import-btn {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.import-btn:hover {
  background: #218838;
  border-color: #1e7e34;
}

/* 性能测试样式 */
.performance-section {
  padding: 20px;
}

.performance-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.performance-results {
  margin-top: 24px;
}

.results-table {
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  overflow: hidden;
  background: white;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  background: #f8f9fa;
  border-bottom: 1px solid #e1e5e9;
  font-weight: 600;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  border-bottom: 1px solid #e1e5e9;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:nth-child(even) {
  background: #f8f9fa;
}

.col {
  padding: 12px 16px;
  text-align: left;
}

.col:not(:first-child) {
  text-align: center;
}

.font-bold {
  font-weight: 600;
}
</style>