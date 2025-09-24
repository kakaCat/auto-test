/**
 * Element Plus 图标统一导入文件
 * 
 * 功能说明：
 * - 统一管理项目中使用的Element Plus图标
 * - 避免在各个组件中重复导入
 * - 提供类型安全的图标引用
 * - 便于图标的统一管理和维护
 * 
 * 使用方式：
 * import { Plus, Edit, Delete } from '@/utils/icons'
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024
 */

// 导出项目中实际使用的Element Plus图标
export {
  // 基础操作图标
  Plus,
  Edit,
  Delete,
  Search,
  Refresh,
  Close,
  Check,
  
  // 文档和文件图标
  Document,
  DocumentAdd,
  CopyDocument,
  FolderOpened,
  
  // 上传下载图标
  Upload,
  Download,
  
  // 箭头和导航图标
  ArrowDown,
  ArrowRight,
  
  // 系统和设备图标
  Monitor,
  Phone,
  Cpu,
  Platform,
  
  // 网络和连接图标
  Link,
  Connection,
  Cloudy,
  
  // 数据和图表图标
  DataBoard,
  Grid,
  Filter,
  
  // 媒体控制图标
  VideoPlay,
  
  // 更多操作图标
  MoreFilled,
  Setting,
  
  // 状态图标
  View,
  Switch
} from '@element-plus/icons-vue'

// 导出图标类型（用于TypeScript类型检查）
export type IconComponent = any