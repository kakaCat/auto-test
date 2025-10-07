<template>
  <div class="workflow-orchestration">
    <div class="page-header">
      <div class="header-content">
        <h1>工作流编排</h1>
        <p>可视化工作流设计和编排，支持多种节点类型和连接方式</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="openDesigner"
        >
          <el-icon><Setting /></el-icon>
          可视化设计器
        </el-button>
        <el-button @click="createWorkflow">
          <el-icon><Plus /></el-icon>
          新建工作流
        </el-button>
        <el-button @click="importWorkflow">
          <el-icon><Upload /></el-icon>
          导入工作流
        </el-button>
        <el-button @click="showTemplates">
          <el-icon><Document /></el-icon>
          模板库
        </el-button>
      </div>
    </div>
    

    
    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索工作流名称或描述"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="状态"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option 
            v-for="status in workflowStatusOptions" 
            :key="status.value" 
            :label="status.label" 
            :value="status.value" 
          />
        </el-select>
        
        <el-select
          v-model="searchForm.category"
          placeholder="分类"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option 
            v-for="category in workflowCategoryOptions" 
            :key="category.value" 
            :label="category.label" 
            :value="category.value" 
          />
        </el-select>
        
        <el-button
          type="primary"
          @click="handleSearch"
        >
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>
    
    <!-- 工作流列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="workflowList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="55"
        />
        
        <el-table-column
          prop="name"
          label="工作流名称"
          min-width="150"
        >
          <template #default="{ row }">
            <div class="workflow-name">
              <span class="name">{{ row.name }}</span>
              <el-tag
                v-if="row.version"
                size="small"
                type="info"
              >
                v{{ row.version }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="category"
          label="分类"
          width="100"
        >
          <template #default="{ row }">
            <el-tag
              :type="getCategoryColor(row.category)"
              size="small"
            >
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="nodeCount"
          label="节点数"
          width="80"
        />
        
        <el-table-column
          prop="description"
          label="描述"
          min-width="200"
          show-overflow-tooltip
        />
        
        <el-table-column
          prop="status"
          label="状态"
          width="100"
        >
          <template #default="{ row }">
            <div class="status-indicator">
              <el-tag
                :type="getStatusColor(row.status)"
                size="small"
              >
                {{ getStatusLabel(row.status) }}
              </el-tag>
              <div
                v-if="row.status === 'running'"
                class="running-indicator"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="executionCount"
          label="执行次数"
          width="100"
        />
        
        <el-table-column
          prop="successRate"
          label="成功率"
          width="100"
        >
          <template #default="{ row }">
            <div class="success-rate">
              <span>{{ row.successRate }}%</span>
              <el-progress
                :percentage="row.successRate"
                :stroke-width="4"
                :show-text="false"
                :color="getProgressColor(row.successRate)"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="lastExecutionTime"
          label="最后执行"
          width="150"
        >
          <template #default="{ row }">
            {{ formatTime(row.lastExecutionTime) }}
          </template>
        </el-table-column>
        
        <el-table-column
          prop="creator"
          label="创建者"
          width="100"
        />
        
        <el-table-column
          label="操作"
          width="280"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="text"
              @click="viewWorkflow(row)"
            >
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button
              type="text"
              @click="editWorkflow(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              v-if="row.status !== 'running'"
              type="text" 
              @click="executeWorkflow(row)"
            >
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button 
              v-else
              type="text" 
              style="color: var(--warning-color)"
              @click="stopWorkflow(row)"
            >
              <el-icon><VideoPause /></el-icon>
              停止
            </el-button>
            <el-button
              type="text"
              @click="copyWorkflow(row)"
            >
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button
              type="text"
              style="color: var(--danger-color)"
              @click="deleteWorkflow(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
    
    <!-- 批量操作 -->
    <div
      v-if="selectedWorkflows.length > 0"
      class="batch-actions"
    >
      <span>已选择 {{ selectedWorkflows.length }} 项</span>
      <el-button @click="batchExecute">
        批量执行
      </el-button>
      <el-button @click="batchStop">
        批量停止
      </el-button>
      <el-button @click="batchPublish">
        批量发布
      </el-button>
      <el-button
        type="danger"
        @click="batchDelete"
      >
        批量删除
      </el-button>
    </div>
    
    <!-- 新建工作流对话框 -->
    <el-dialog
      v-model="createWorkflowDialogVisible"
      title="新建工作流"
      width="800px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <!-- 步骤指示器 -->
      <el-steps
        :active="currentStep"
        align-center
        class="create-steps"
      >
        <el-step
          title="基本信息"
          description="填写工作流基本信息"
        />
        <el-step
          title="创建方式"
          description="选择创建方式"
        />
        <el-step
          title="完成创建"
          description="确认并创建工作流"
        />
      </el-steps>

      <!-- 步骤内容 -->
      <div class="step-content">
        <!-- 步骤1: 基本信息 -->
        <div
          v-if="currentStep === 0"
          class="step-basic-info"
        >
          <el-form
            ref="workflowFormRef"
            :model="workflowForm"
            :rules="workflowRules"
            label-width="100px"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  label="工作流名称"
                  prop="name"
                >
                  <el-input
                    v-model="workflowForm.name"
                    placeholder="请输入工作流名称"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  label="分类"
                  prop="category"
                >
                  <el-select
                    v-model="workflowForm.category"
                    placeholder="请选择分类"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="category in workflowCategoryOptions"
                      :key="category.value"
                      :label="category.label"
                      :value="category.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item
              label="描述"
              prop="description"
            >
              <el-input
                v-model="workflowForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入工作流描述"
              />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  label="优先级"
                  prop="priority"
                >
                  <el-select
                    v-model="workflowForm.priority"
                    placeholder="请选择优先级"
                    style="width: 100%"
                  >
                    <el-option
                      label="低"
                      value="low"
                    />
                    <el-option
                      label="中"
                      value="medium"
                    />
                    <el-option
                      label="高"
                      value="high"
                    />
                    <el-option
                      label="紧急"
                      value="urgent"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  label="超时设置"
                  prop="timeout"
                >
                  <el-input-number 
                    v-model="workflowForm.timeout" 
                    :min="1" 
                    :max="3600" 
                    placeholder="秒"
                    style="width: 100%"
                  />
                  <span style="margin-left: 8px; color: #909399; font-size: 12px">秒</span>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  label="关联应用"
                  prop="frontendApp"
                >
                  <el-select
                    v-model="workflowForm.frontendApp"
                    placeholder="请选择前端应用"
                    clearable
                    style="width: 100%"
                  >
                    <el-option
                      v-for="app in frontendAppOptions"
                      :key="app.value"
                      :label="app.label"
                      :value="app.value"
                    >
                      <span style="float: left">{{ app.label }}</span>
                      <span style="float: right; color: #8492a6; font-size: 13px">{{ app.description }}</span>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  label="执行环境"
                  prop="environment"
                >
                  <el-select
                    v-model="workflowForm.environment"
                    placeholder="请选择执行环境"
                    style="width: 100%"
                  >
                    <el-option
                      label="开发环境"
                      value="development"
                    />
                    <el-option
                      label="测试环境"
                      value="testing"
                    />
                    <el-option
                      label="预发布环境"
                      value="staging"
                    />
                    <el-option
                      label="生产环境"
                      value="production"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="标签">
              <el-input
                v-model="workflowForm.tags"
                placeholder="请输入标签，多个标签用逗号分隔"
              />
            </el-form-item>
            
            <el-form-item label="自动保存">
              <el-switch 
                v-model="workflowForm.autoSave" 
                active-text="开启" 
                inactive-text="关闭"
              />
              <span style="margin-left: 8px; color: #909399; font-size: 12px">开启后将自动保存工作流草稿</span>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤2: 创建方式 -->
        <div
          v-if="currentStep === 1"
          class="step-create-method"
        >
          <div class="create-methods">
            <div
              class="method-card"
              :class="{ active: selectedMethod === 'blank' }"
              @click="selectedMethod = 'blank'"
            >
              <el-icon class="method-icon">
                <Document />
              </el-icon>
              <h3>从空白开始</h3>
              <p>创建一个空白工作流，从零开始设计</p>
              <div class="method-features">
                <el-tag
                  size="small"
                  type="info"
                >
                  完全自定义
                </el-tag>
                <el-tag
                  size="small"
                  type="success"
                >
                  灵活度高
                </el-tag>
              </div>
            </div>
            <div
              class="method-card"
              :class="{ active: selectedMethod === 'template' }"
              @click="selectedMethod = 'template'"
            >
              <el-icon class="method-icon">
                <Collection />
              </el-icon>
              <h3>从模板创建</h3>
              <p>基于现有模板快速创建工作流</p>
              <div class="method-features">
                <el-tag
                  size="small"
                  type="primary"
                >
                  快速开始
                </el-tag>
                <el-tag
                  size="small"
                  type="warning"
                >
                  最佳实践
                </el-tag>
              </div>
            </div>
            <div
              class="method-card"
              :class="{ active: selectedMethod === 'import' }"
              @click="selectedMethod = 'import'"
            >
              <el-icon class="method-icon">
                <Upload />
              </el-icon>
              <h3>导入工作流</h3>
              <p>导入已有的工作流文件</p>
              <div class="method-features">
                <el-tag
                  size="small"
                  type="success"
                >
                  复用现有
                </el-tag>
                <el-tag
                  size="small"
                  type="info"
                >
                  批量导入
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 模板选择 -->
          <div
            v-if="selectedMethod === 'template'"
            class="template-selection"
          >
            <div class="template-header">
              <h4>选择模板</h4>
              <el-input
                v-model="templateSearchKeyword"
                placeholder="搜索模板..."
                style="width: 200px"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
            <div class="templates-grid">
              <div
                v-for="template in filteredTemplates"
                :key="template.id"
                class="template-card"
                :class="{ selected: selectedTemplate === template.id }"
                @click="selectedTemplate = template.id"
              >
                <div class="template-icon">
                  <el-icon><component :is="template.icon" /></el-icon>
                </div>
                <div class="template-content">
                  <h5>{{ template.name }}</h5>
                  <p>{{ template.description }}</p>
                  <div class="template-meta">
                    <span>{{ template.nodeCount }} 个节点</span>
                    <span>{{ template.usageCount }} 次使用</span>
                  </div>
                  <div class="template-actions">
                    <el-button
                      size="small"
                      type="text"
                      @click.stop="previewTemplate(template)"
                    >
                      <el-icon><View /></el-icon>
                      预览
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 模板预览对话框 -->
            <el-dialog
              v-model="templatePreviewVisible"
              title="模板预览"
              width="60%"
              :close-on-click-modal="false"
            >
              <div
                v-if="previewingTemplate"
                class="template-preview"
              >
                <div class="preview-header">
                  <h3>{{ previewingTemplate.name }}</h3>
                  <p>{{ previewingTemplate.description }}</p>
                </div>
                <div class="preview-content">
                  <div class="preview-info">
                    <el-descriptions
                      :column="2"
                      border
                    >
                      <el-descriptions-item label="节点数量">
                        {{ previewingTemplate.nodeCount }}
                      </el-descriptions-item>
                      <el-descriptions-item label="使用次数">
                        {{ previewingTemplate.usageCount }}
                      </el-descriptions-item>
                      <el-descriptions-item label="分类">
                        {{ getCategoryLabel(previewingTemplate.category) }}
                      </el-descriptions-item>
                      <el-descriptions-item label="适用场景">
                        {{ getTemplateScenario(previewingTemplate.category) }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                  <div class="preview-workflow">
                    <h4>工作流结构预览</h4>
                    <div class="workflow-preview-placeholder">
                      <el-icon size="48">
                        <DataAnalysis />
                      </el-icon>
                      <p>工作流结构图</p>
                      <small>{{ previewingTemplate.name }} 的节点连接图</small>
                    </div>
                  </div>
                </div>
              </div>
              <template #footer>
                <el-button @click="templatePreviewVisible = false">
                  关闭
                </el-button>
                <el-button
                  type="primary"
                  @click="selectTemplateFromPreview"
                >
                  选择此模板
                </el-button>
              </template>
            </el-dialog>
          </div>

          <!-- 文件导入 -->
          <div
            v-if="selectedMethod === 'import'"
            class="file-import"
          >
            <div class="import-options">
              <el-radio-group
                v-model="importType"
                class="import-type-group"
              >
                <el-radio label="file">
                  文件导入
                </el-radio>
                <el-radio label="url">
                  URL导入
                </el-radio>
                <el-radio label="text">
                  文本导入
                </el-radio>
              </el-radio-group>
            </div>
            
            <!-- 文件上传 -->
            <div
              v-if="importType === 'file'"
              class="file-upload"
            >
              <el-upload
                class="upload-demo"
                drag
                :auto-upload="false"
                :on-change="handleFileChange"
                accept=".json,.yaml,.yml"
              >
                <el-icon class="el-icon--upload">
                  <upload-filled />
                </el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 JSON、YAML 格式的工作流文件，最大 10MB
                  </div>
                </template>
              </el-upload>
            </div>
            
            <!-- URL导入 -->
            <div
              v-if="importType === 'url'"
              class="url-import"
            >
              <el-input
                v-model="importUrl"
                placeholder="请输入工作流文件的URL地址"
                clearable
              >
                <template #prepend>
                  URL
                </template>
                <template #append>
                  <el-button @click="validateImportUrl">
                    验证
                  </el-button>
                </template>
              </el-input>
            </div>
            
            <!-- 文本导入 -->
            <div
              v-if="importType === 'text'"
              class="text-import"
            >
              <el-input
                v-model="importText"
                type="textarea"
                :rows="8"
                placeholder="请粘贴工作流的JSON或YAML内容"
              />
              <div class="import-actions">
                <el-button @click="formatImportText">
                  格式化
                </el-button>
                <el-button @click="validateImportText">
                  验证
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤3: 完成创建 -->
        <div
          v-if="currentStep === 2"
          class="step-confirm"
        >
          <div class="confirm-info">
            <h3>确认创建工作流</h3>
            <el-descriptions
              :column="2"
              border
            >
              <el-descriptions-item label="工作流名称">
                {{ workflowForm.name }}
              </el-descriptions-item>
              <el-descriptions-item label="分类">
                <el-tag :type="getCategoryColor(workflowForm.category)">
                  {{ getCategoryLabel(workflowForm.category) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityColor(workflowForm.priority)">
                  {{ getPriorityLabel(workflowForm.priority) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="超时设置">
                {{ workflowForm.timeout }} 秒
              </el-descriptions-item>
              <el-descriptions-item label="执行环境">
                <el-tag :type="getEnvironmentColor(workflowForm.environment)">
                  {{ getEnvironmentLabel(workflowForm.environment) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="关联应用">
                {{ getFrontendAppLabel(workflowForm.frontendApp) || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="创建方式">
                <el-tag type="info">
                  {{ getMethodLabel(selectedMethod) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="自动保存">
                <el-tag :type="workflowForm.autoSave ? 'success' : 'info'">
                  {{ workflowForm.autoSave ? '开启' : '关闭' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item
                label="描述"
                :span="2"
              >
                {{ workflowForm.description }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="workflowForm.tags"
                label="标签"
                :span="2"
              >
                <el-tag 
                  v-for="tag in workflowForm.tags.split(',').filter(t => t.trim())" 
                  :key="tag.trim()" 
                  size="small" 
                  style="margin-right: 8px"
                >
                  {{ tag.trim() }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item
                v-if="selectedMethod === 'template' && selectedTemplate"
                label="选择模板"
                :span="2"
              >
                {{ getTemplateName(selectedTemplate) }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="creation-tips">
              <el-alert
                title="创建提示"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <ul>
                    <li>工作流创建后将自动跳转到可视化设计器</li>
                    <li v-if="workflowForm.autoSave">
                      已开启自动保存，设计过程中会自动保存草稿
                    </li>
                    <li v-if="selectedMethod === 'template'">
                      基于模板创建的工作流可以进一步自定义
                    </li>
                    <li>可以随时在工作流列表中管理和编辑工作流</li>
                  </ul>
                </template>
              </el-alert>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelCreate">
            取消
          </el-button>
          <el-button
            v-if="currentStep > 0"
            @click="prevStep"
          >
            上一步
          </el-button>
          <el-button
            v-if="currentStep < 2"
            type="primary"
            @click="nextStep"
          >
            下一步
          </el-button>
          <el-button
            v-if="currentStep === 2"
            type="primary"
            :loading="creating"
            @click="confirmCreate"
          >
            创建工作流
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 模板库对话框 -->
    <el-dialog
      v-model="templatesDialogVisible"
      title="工作流模板库"
      width="800px"
    >
      <div class="templates-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          @click="useTemplate(template)"
        >
          <div class="template-icon">
            <el-icon>
              <component :is="template.icon" />
            </el-icon>
          </div>
          <div class="template-content">
            <h3>{{ template.name }}</h3>
            <p>{{ template.description }}</p>
            <div class="template-meta">
              <span class="node-count">{{ template.nodeCount }} 个节点</span>
              <span class="usage-count">使用 {{ template.usageCount }} 次</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="templatesDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Upload, 
  Document, 
  Search, 
  Collection,
  UploadFilled,
  Setting
} from '@element-plus/icons-vue'
import workflowApiModule from '@/api/workflow'

const workflowApi = workflowApiModule.workflow
import {
  workflowStatusOptions,
  workflowCategoryOptions,
  defaultSearchForm,
  defaultPagination,

  workflowTableColumns,
  getStatusColor,
  getStatusLabel,
  getProgressColor,
  formatTime,
  workflowTemplates
} from './data/index'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const templatesDialogVisible = ref(false)
const workflowList = ref([])
const selectedWorkflows = ref([])

// 新建工作流对话框相关
const createWorkflowDialogVisible = ref(false)
const currentStep = ref(0)
const creating = ref(false)
const selectedMethod = ref('blank')
const selectedTemplate = ref(null)
const workflowFormRef = ref(null)

// 模板相关
const templateSearchKeyword = ref('')
const templatePreviewVisible = ref(false)
const previewingTemplate = ref(null)

// 导入相关
const importType = ref('file')
const importUrl = ref('')
const importText = ref('')

// 前端应用选项
const frontendAppOptions = ref([
  {
    value: 'admin-dashboard',
    label: '管理后台',
    description: '系统管理后台应用'
  },
  {
    value: 'user-portal',
    label: '用户门户',
    description: '面向用户的门户应用'
  },
  {
    value: 'mobile-app',
    label: '移动应用',
    description: '移动端应用'
  },
  {
    value: 'api-docs',
    label: 'API文档',
    description: 'API文档站点'
  },
  {
    value: 'monitoring',
    label: '监控面板',
    description: '系统监控面板'
  }
])

// 工作流表单数据
const workflowForm = reactive({
  name: '',
  description: '',
  category: '',
  priority: 'medium',
  timeout: 300,
  frontendApp: '',
  environment: 'development',
  tags: '',
  autoSave: true
})

// 表单验证规则
const workflowRules = {
  name: [
    { required: true, message: '请输入工作流名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入工作流描述', trigger: 'blur' },
    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择工作流分类', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  timeout: [
    { required: true, message: '请设置超时时间', trigger: 'blur' },
    { type: 'number', min: 1, max: 3600, message: '超时时间必须在1-3600秒之间', trigger: 'blur' }
  ],
  environment: [
    { required: true, message: '请选择执行环境', trigger: 'change' }
  ]
}



// 搜索表单
const searchForm = reactive({ ...defaultSearchForm })

// 分页
const pagination = reactive({ ...defaultPagination })

// 模板数据
const templates = ref(workflowTemplates)

// 过滤后的模板
const filteredTemplates = computed(() => {
  if (!templateSearchKeyword.value) {
    return templates.value
  }
  return templates.value.filter(template => 
    template.name.toLowerCase().includes(templateSearchKeyword.value.toLowerCase()) ||
    template.description.toLowerCase().includes(templateSearchKeyword.value.toLowerCase())
  )
})

// 获取分类标签
const getCategoryLabel = (category) => {
  const labelMap = {
    'api-test': 'API测试',
    'data-processing': '数据处理',
    'auto-deploy': '自动化部署',
    'monitoring': '监控告警',
    'data-sync': '数据同步',
    'other': '其他'
  }
  return labelMap[category] || category
}

// 获取分类颜色
const getCategoryColor = (category) => {
  const colorMap = {
    'api-test': 'primary',
    'data-processing': 'success',
    'auto-deploy': 'warning',
    'monitoring': 'danger',
    'data-sync': 'info',
    'other': 'info'
  }
  return colorMap[category] || 'info'
}

// 获取优先级标签
const getPriorityLabel = (priority) => {
  const labelMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'urgent': '紧急'
  }
  return labelMap[priority] || priority
}

// 获取优先级颜色
const getPriorityColor = (priority) => {
  const colorMap = {
    'low': 'info',
    'medium': 'primary',
    'high': 'warning',
    'urgent': 'danger'
  }
  return colorMap[priority] || 'info'
}

// 获取环境标签
const getEnvironmentLabel = (environment) => {
  const labelMap = {
    'development': '开发环境',
    'testing': '测试环境',
    'staging': '预发布环境',
    'production': '生产环境'
  }
  return labelMap[environment] || environment
}

// 获取环境颜色
const getEnvironmentColor = (environment) => {
  const colorMap = {
    'development': 'info',
    'testing': 'primary',
    'staging': 'warning',
    'production': 'success'
  }
  return colorMap[environment] || 'info'
}

// 获取前端应用标签
const getFrontendAppLabel = (appValue) => {
  const app = frontendAppOptions.value.find(option => option.value === appValue)
  return app ? app.label : ''
}

// 打开可视化设计器
const openDesigner = () => {
  // 使用路由导航到设计器页面
  router.push('/workflow-orchestration/designer')
}

// 创建工作流
const createWorkflow = () => {
  createWorkflowDialogVisible.value = true
  resetCreateForm()
  
  // 尝试加载草稿数据
  setTimeout(() => {
    const hasDraft = loadDraftData()
    if (hasDraft) {
      ElMessageBox.confirm(
        '检测到未完成的工作流草稿，是否继续编辑？',
        '恢复草稿',
        {
          confirmButtonText: '继续编辑',
          cancelButtonText: '重新开始',
          type: 'info'
        }
      ).catch(() => {
        // 用户选择重新开始，清除草稿
        clearDraftData()
        resetCreateForm()
      })
    }
  }, 100)
}

// 重置创建表单
const resetCreateForm = () => {
  currentStep.value = 0
  selectedMethod.value = 'blank'
  selectedTemplate.value = null
  creating.value = false
  Object.assign(workflowForm, {
    name: '',
    description: '',
    category: '',
    frontendApp: '',
    tags: ''
  })
  if (workflowFormRef.value) {
    workflowFormRef.value.clearValidate()
  }
}

// 加载草稿数据
const loadDraftData = () => {
  try {
    // 查找最新的草稿
    const draftKeys = Object.keys(localStorage).filter(key => key.startsWith('workflow_draft_'))
    if (draftKeys.length === 0) return false

    // 按时间戳排序，获取最新的草稿
    const latestDraftKey = draftKeys.sort().pop()
    const draftData = JSON.parse(localStorage.getItem(latestDraftKey))

    if (draftData && draftData.data) {
      // 恢复基本信息
      if (draftData.step >= 0 && draftData.data.name) {
        workflowForm.name = draftData.data.name || ''
        workflowForm.description = draftData.data.description || ''
        workflowForm.category = draftData.data.category || ''
        workflowForm.frontendApp = draftData.data.frontendApp || ''
        workflowForm.tags = draftData.data.tags || ''
      }

      // 恢复创建方式
      if (draftData.step >= 1) {
        selectedMethod.value = draftData.data.createMethod || 'blank'
        selectedTemplate.value = draftData.data.templateId || null
      }

      // 设置当前步骤
      currentStep.value = Math.min(draftData.step, 2)
      
      ElMessage.success('已恢复上次保存的草稿')
      return true
    }
  } catch (error) {
    console.warn('加载草稿失败:', error)
  }
  return false
}

// 清除草稿数据
const clearDraftData = () => {
  const draftKeys = Object.keys(localStorage).filter(key => key.startsWith('workflow_draft_'))
  draftKeys.forEach(key => localStorage.removeItem(key))
}

// 保存当前步骤数据
const saveCurrentStep = async () => {
  try {
    const stepData = {
      step: currentStep.value,
      data: {}
    }

    if (currentStep.value === 0) {
      // 保存基本信息
      stepData.data = {
        name: workflowForm.name,
        description: workflowForm.description,
        category: workflowForm.category,
        frontendApp: workflowForm.frontendApp,
        tags: workflowForm.tags
      }
    } else if (currentStep.value === 1) {
      // 保存创建方式
      stepData.data = {
        createMethod: selectedMethod.value,
        templateId: selectedTemplate.value
      }
    }

    // 保存到本地存储作为草稿
    const draftKey = `workflow_draft_${Date.now()}`
    localStorage.setItem(draftKey, JSON.stringify(stepData))
    
    ElMessage.success('当前步骤已自动保存')
    return true
  } catch (error) {
    ElMessage.warning('保存失败：' + (error.message || '未知错误'))
    return false
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 0) {
    // 验证基本信息表单
    if (!workflowFormRef.value) return
    try {
      await workflowFormRef.value.validate()
      // 保存当前步骤
      const saved = await saveCurrentStep()
      if (saved) {
        currentStep.value++
      }
    } catch (error) {
      ElMessage.warning('请完善基本信息')
    }
  } else if (currentStep.value === 1) {
    // 验证创建方式选择
    if (!selectedMethod.value) {
      ElMessage.warning('请选择创建方式')
      return
    }
    if (selectedMethod.value === 'template' && !selectedTemplate.value) {
      ElMessage.warning('请选择模板')
      return
    }
    // 保存当前步骤
    const saved = await saveCurrentStep()
    if (saved) {
      currentStep.value++
    }
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 取消创建
const cancelCreate = () => {
  createWorkflowDialogVisible.value = false
  resetCreateForm()
}

// 确认创建
const confirmCreate = async () => {
  creating.value = true
  try {
    const workflowData = {
      ...workflowForm,
      tags: workflowForm.tags ? workflowForm.tags.split(',').map(tag => tag.trim()) : [],
      createMethod: selectedMethod.value,
      templateId: selectedTemplate.value
    }

    // 调用API创建工作流
    const response = await workflowApi.createWorkflow(workflowData)
    
    ElMessage.success('工作流创建成功')
    
    // 清除草稿数据
    clearDraftData()
    
    createWorkflowDialogVisible.value = false
    resetCreateForm()
    
    // 跳转到工作流设计器
    router.push(`/workflow-orchestration/designer/${response.data.id}`)
    
  } catch (error) {
    ElMessage.error('创建工作流失败：' + (error.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

// 获取创建方式标签
const getMethodLabel = (method) => {
  const labelMap = {
    'blank': '从空白开始',
    'template': '从模板创建',
    'import': '导入工作流'
  }
  return labelMap[method] || method
}

// 获取模板名称
const getTemplateName = (templateId) => {
  const template = templates.value.find(t => t.id === templateId)
  return template ? template.name : ''
}

// 处理文件变更
const handleFileChange = (file) => {
  // 处理文件导入逻辑
  console.log('文件变更:', file)
}

// 预览模板
const previewTemplate = (template) => {
  previewingTemplate.value = template
  templatePreviewVisible.value = true
}

// 从预览中选择模板
const selectTemplateFromPreview = () => {
  if (previewingTemplate.value) {
    selectedTemplate.value = previewingTemplate.value.id
    templatePreviewVisible.value = false
    ElMessage.success(`已选择模板：${previewingTemplate.value.name}`)
  }
}

// 获取模板适用场景
const getTemplateScenario = (category) => {
  const scenarioMap = {
    'api-test': 'API接口测试、自动化测试',
    'data-processing': '数据处理、ETL流程',
    'auto-deploy': '自动化部署、CI/CD',
    'monitoring': '系统监控、告警通知',
    'data-sync': '数据同步、数据迁移',
    'other': '通用场景'
  }
  return scenarioMap[category] || '通用场景'
}

// 验证导入URL
const validateImportUrl = async () => {
  if (!importUrl.value) {
    ElMessage.warning('请输入URL地址')
    return
  }
  
  try {
    ElMessage.info('正在验证URL...')
    // 这里可以添加URL验证逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('URL验证成功')
  } catch (error) {
    ElMessage.error('URL验证失败：' + (error.message || '无法访问该URL'))
  }
}

// 格式化导入文本
const formatImportText = () => {
  if (!importText.value) {
    ElMessage.warning('请输入要格式化的内容')
    return
  }
  
  try {
    const parsed = JSON.parse(importText.value)
    importText.value = JSON.stringify(parsed, null, 2)
    ElMessage.success('格式化成功')
  } catch (error) {
    ElMessage.error('格式化失败：内容不是有效的JSON格式')
  }
}

// 验证导入文本
const validateImportText = () => {
  if (!importText.value) {
    ElMessage.warning('请输入要验证的内容')
    return
  }
  
  try {
    JSON.parse(importText.value)
    ElMessage.success('内容验证成功')
  } catch (error) {
    ElMessage.error('内容验证失败：' + error.message)
  }
}

// 查看工作流
const viewWorkflow = (row) => {
  router.push(`/workflow-orchestration/view/${row.id}`)
}

// 编辑工作流
const editWorkflow = (row) => {
  router.push(`/workflow-orchestration/designer/${row.id}`)
}

// 执行工作流
const executeWorkflow = async (row) => {
  try {
    ElMessage.info('开始执行工作流...')
    
    // 这里调用执行API
    console.log('执行工作流:', row)
    
    // 更新状态
    row.status = 'running'
    
    ElMessage.success('工作流执行已启动')
    
    // 跳转到执行监控页面
    router.push(`/workflow-orchestration/monitor/${row.id}`)
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  }
}

// 停止工作流
const stopWorkflow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止工作流 "${row.name}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用停止API
    console.log('停止工作流:', row)
    
    // 更新状态
    row.status = 'stopped'
    
    ElMessage.success('工作流已停止')
  } catch (error) {
    // 用户取消停止
  }
}

// 复制工作流
const copyWorkflow = async (row) => {
  try {
    // 这里调用复制API
    console.log('复制工作流:', row)
    
    ElMessage.success('工作流复制成功')
    loadWorkflowList()
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 删除工作流
const deleteWorkflow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除工作流 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用删除API
    console.log('删除工作流:', row)
    
    ElMessage.success('删除成功')
    loadWorkflowList()
  } catch (error) {
    // 用户取消删除
  }
}

// 选择变更
const handleSelectionChange = (selection) => {
  selectedWorkflows.value = selection
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadWorkflowList()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    category: ''
  })
  handleSearch()
}

// 分页变更
const handlePageChange = (page) => {
  pagination.page = page
  loadWorkflowList()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadWorkflowList()
}

// 批量操作
const batchExecute = () => {
  console.log('批量执行:', selectedWorkflows.value)
  ElMessage.success('批量执行已启动')
}

const batchStop = () => {
  console.log('批量停止:', selectedWorkflows.value)
  ElMessage.success('批量停止成功')
}

const batchPublish = () => {
  console.log('批量发布:', selectedWorkflows.value)
  ElMessage.success('批量发布成功')
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedWorkflows.value.length} 个工作流吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('批量删除:', selectedWorkflows.value)
    ElMessage.success('批量删除成功')
    loadWorkflowList()
  } catch (error) {
    // 用户取消删除
  }
}

// 导入工作流
const importWorkflow = () => {
  ElMessage.info('导入功能开发中...')
}

// 显示模板库
const showTemplates = () => {
  templatesDialogVisible.value = true
}

// 使用模板
const useTemplate = (template) => {
  templatesDialogVisible.value = false
  router.push(`/workflow-orchestration/designer/new?template=${template.id}`)
}

// 加载工作流列表
const loadWorkflowList = async () => {
  loading.value = true
  try {
    const response = await workflowApi.getWorkflowList({
      keyword: searchForm.keyword,
      status: searchForm.status,
      category: searchForm.category,
      page: pagination.page,
      // 兼容旧参数名：后端适配层会处理 page_size
      pageSize: pagination.size
    })
    
    if (response.success) {
      const list = Array.isArray(response.data) ? response.data : (response.data?.list ?? [])
      workflowList.value = list
      const totalVal = typeof (response?.data?.total) === 'number' 
        ? response.data.total 
        : list.length
      pagination.total = totalVal
    } else {
      ElMessage.error(response.message || '加载工作流列表失败')
    }
  } catch (error) {
    console.error('加载工作流列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}



onMounted(() => {
  loadWorkflowList()
})
</script>

<style scoped>
.workflow-orchestration {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.header-content p {
  color: var(--text-color-regular);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}



.search-section {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.table-section {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
}

.workflow-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 500;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.running-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.success-rate {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.success-rate span {
  font-size: 12px;
  color: var(--text-color-regular);
}

.pagination-wrapper {
  padding: 16px;
  display: flex;
  justify-content: center;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 12px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.template-card {
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
}

.template-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.template-content {
  flex: 1;
}

.template-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.template-content p {
  font-size: 14px;
  color: var(--text-color-regular);
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-color-placeholder);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .workflow-orchestration {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  

  
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-form > * {
    width: 100% !important;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
}

/* 新建工作流对话框样式 */
.create-steps {
  margin-bottom: 30px;
}

.step-content {
  min-height: 300px;
  padding: 20px 0;
}

.step-basic-info .el-form {
  max-width: 500px;
  margin: 0 auto;
}

.step-create-method {
  text-align: center;
}

.create-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.method-card {
  border: 2px solid var(--border-color-lighter);
  border-radius: 12px;
  padding: 24px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-color-overlay);
}

.method-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.method-card.active {
  border-color: var(--color-primary);
  background: rgba(64, 158, 255, 0.05);
}

.method-icon {
  font-size: 32px;
  color: var(--color-primary);
  margin-bottom: 12px;
}

.method-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.method-card p {
  font-size: 14px;
  color: var(--text-color-regular);
  margin: 0;
  line-height: 1.4;
}

.template-selection {
  margin-top: 30px;
  text-align: left;
}

.template-selection h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 16px 0;
}

.template-selection .templates-grid {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}

.template-selection .template-card {
  border: 2px solid var(--border-color-lighter);
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-selection .template-card:hover {
  border-color: var(--color-primary);
}

.template-selection .template-card.selected {
  border-color: var(--color-primary);
  background: rgba(64, 158, 255, 0.05);
}

.template-selection .template-content h5 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 4px 0;
}

.template-selection .template-content p {
  font-size: 12px;
  color: var(--text-color-regular);
  margin: 0 0 8px 0;
}

.template-selection .template-meta {
  font-size: 11px;
  color: var(--text-color-placeholder);
}

.file-import {
  margin-top: 30px;
}

.step-confirm {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}

.confirm-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 20px 0;
  text-align: center;
}

.creation-tips {
  margin-top: 24px;
}

.creation-tips ul {
  margin: 0;
  padding-left: 20px;
}

.creation-tips li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 - 新建工作流对话框 */
@media (max-width: 768px) {
  .create-methods {
    grid-template-columns: 1fr;
  }
  
  .template-selection .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .step-basic-info .el-form,
  .step-confirm {
    max-width: 100%;
  }
}
</style>