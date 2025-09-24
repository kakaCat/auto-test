/**
 * 工作流编排页面模板配置
 */
import { Component } from 'vue'
import { 
  DataAnalysis, 
  Monitor, 
  Upload, 
  Download, 
  Setting, 
  Connection,
  Timer,
  Bell
} from '@element-plus/icons-vue'

// 工作流模板接口定义
export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  icon: Component
  nodeCount: number
  usageCount: number
  category: 'api-test' | 'data-sync' | 'monitoring' | 'auto-deploy' | 'data-processing' | 'other'
}

// 工作流模板配置
export const workflowTemplates: WorkflowTemplate[] = [
  {
    id: 'api-test-template',
    name: 'API自动化测试',
    description: '包含API请求、断言验证、数据提取等节点的完整测试流程',
    icon: DataAnalysis,
    nodeCount: 8,
    usageCount: 156,
    category: 'api-test'
  },
  {
    id: 'data-sync-template',
    name: '数据同步流程',
    description: '数据库间数据同步，支持增量同步和全量同步',
    icon: Connection,
    nodeCount: 6,
    usageCount: 89,
    category: 'data-sync'
  },
  {
    id: 'monitoring-template',
    name: '监控告警流程',
    description: '系统监控、异常检测、告警通知的完整流程',
    icon: Monitor,
    nodeCount: 10,
    usageCount: 234,
    category: 'monitoring'
  },
  {
    id: 'deploy-template',
    name: '自动化部署',
    description: '代码构建、测试、部署的CI/CD流程模板',
    icon: Upload,
    nodeCount: 12,
    usageCount: 67,
    category: 'auto-deploy'
  },
  {
    id: 'data-processing-template',
    name: '数据处理流程',
    description: '数据清洗、转换、分析的ETL流程模板',
    icon: Setting,
    nodeCount: 9,
    usageCount: 123,
    category: 'data-processing'
  },
  {
    id: 'scheduled-task-template',
    name: '定时任务流程',
    description: '定时执行的任务流程，支持多种触发条件',
    icon: Timer,
    nodeCount: 5,
    usageCount: 78,
    category: 'other'
  },
  {
    id: 'notification-template',
    name: '通知推送流程',
    description: '多渠道消息推送，支持邮件、短信、钉钉等',
    icon: Bell,
    nodeCount: 7,
    usageCount: 145,
    category: 'other'
  },
  {
    id: 'backup-template',
    name: '数据备份流程',
    description: '数据库备份、文件备份的自动化流程',
    icon: Download,
    nodeCount: 6,
    usageCount: 92,
    category: 'other'
  }
]