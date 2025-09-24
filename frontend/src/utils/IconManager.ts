import {
  Search,
  ArrowDown,
  ArrowRight,
  MoreFilled,
  Plus,
  Edit,
  Delete,
  Folder,
  DocumentAdd,
  FolderOpened,
  Document,
  Setting,
  Monitor,
  Platform,
  DataBoard,
  Cloudy,
  Link,
  Phone,
  Connection,
  Cpu,
  Service
} from '@element-plus/icons-vue'

/**
 * 图标管理器
 * 统一管理Element Plus图标，提供静态方法访问
 */
export class IconManager {
  /**
   * 获取所有可用图标
   */
  static getAllIcons() {
    return {
      Search,
      ArrowDown,
      ArrowRight,
      MoreFilled,
      Plus,
      Edit,
      Delete,
      Folder,
      DocumentAdd,
      FolderOpened,
      Document,
      Setting,
      Monitor,
      Platform,
      DataBoard,
      Cloudy,
      Link,
      Phone,
      Connection,
      Cpu,
      Service
    }
  }

  /**
   * 获取系统树相关图标
   */
  static getSystemTreeIcons() {
    return {
      Search,
      ArrowDown,
      ArrowRight,
      MoreFilled,
      Plus,
      Edit,
      Delete,
      Folder,
      DocumentAdd,
      FolderOpened,
      Document,
      Setting
    }
  }

  /**
   * 获取系统类型图标
   */
  static getSystemTypeIcons() {
    return {
      Monitor,
      Platform,
      DataBoard,
      Cloudy,
      Link,
      Phone,
      Connection,
      Cpu,
      Service
    }
  }

  /**
   * 根据图标名称获取图标组件
   */
  static getIconByName(iconName: string) {
    const icons = this.getAllIcons()
    return icons[iconName as keyof typeof icons] || Document
  }

  /**
   * 获取系统默认图标
   */
  static getDefaultSystemIcon() {
    return Monitor
  }

  /**
   * 获取模块默认图标
   */
  static getDefaultModuleIcon() {
    return Document
  }

  /**
   * 获取文件夹图标（展开/收起状态）
   */
  static getFolderIcon(expanded: boolean) {
    return expanded ? FolderOpened : Folder
  }

  /**
   * 获取箭头图标（展开/收起状态）
   */
  static getArrowIcon(expanded: boolean) {
    return expanded ? ArrowDown : ArrowRight
  }
}