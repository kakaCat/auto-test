/**
 * 工具函数
 */

import type { Component } from 'vue'
import {
  Monitor, Connection, MessageBox, User, Setting,
  Document, Lock, DataAnalysis, Service, Menu, Folder
} from '@element-plus/icons-vue'

import { SystemCategory } from '../types'
import type { Module, IconMap, TagTypeMap } from '../types'

// 系统图标映射
const systemIconMap: IconMap = {
  [SystemCategory.BACKEND]: Service,
  [SystemCategory.FRONTEND]: Document
}

// 模块图标映射
const moduleIconMap: Record<string, Component> = {
  'API': Connection,
  '前端': Document,
  '后端': Service,
  '监控': Monitor,
  '管理': Setting,
  '用户': User,
  '文档': Document,
  '安全': Lock,
  '分析': DataAnalysis
}

// 分类标签类型映射
const categoryTagTypeMap: TagTypeMap = {
  [SystemCategory.BACKEND]: 'primary',
  [SystemCategory.FRONTEND]: 'success'
}

/**
 * 获取系统图标
 * @param category 系统分类
 * @returns Vue 组件
 */
export const getSystemIcon = (category: SystemCategory): Component => {
  return systemIconMap[category] || Service
}

/**
 * 获取模块图标
 * @param module 模块对象
 * @returns Vue 组件
 */
export const getModuleIcon = (module: Module): Component => {
  // 根据模块标签判断图标
  if (module.tags && Array.isArray(module.tags)) {
    for (const tag of module.tags) {
      if (moduleIconMap[tag]) {
        return moduleIconMap[tag]
      }
    }
  }
  
  // 根据模块类型判断图标
  if ((module.module_type || '').includes('API')) return Connection
  if ((module.module_type || '').includes('前端')) return Document
  if ((module.module_type || '').includes('后端')) return Service
  if ((module.module_type || '').includes('监控')) return Monitor
  if ((module.module_type || '').includes('管理')) return Setting
  
  // 根据路径判断图标
  if ((module.path || '').includes('/api/')) return Connection
  if ((module.path || '').includes('/admin/')) return Setting
  if ((module.path || '').includes('/user/')) return User
  
  return Folder
}

/**
 * 获取分类标签类型
 * @param category 系统分类
 * @returns 标签类型
 */
export const getCategoryTagType = (category: SystemCategory): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  return categoryTagTypeMap[category] || 'info'
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的大小字符串
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 格式化日期
 * @param date 日期字符串或 Date 对象
 * @returns 格式化后的日期字符串
 */
export const formatDate = (date: string | Date): string => {
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 生成唯一ID
 * @param prefix 前缀
 * @returns 唯一ID字符串
 */
export const generateId = (prefix: string = 'id'): string => {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 深度克隆对象
 * @param obj 要克隆的对象
 * @returns 克隆后的对象
 */
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as unknown as T
  if (typeof obj === 'object') {
    const clonedObj = {} as T
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  return obj
}

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param wait 等待时间（毫秒）
 * @returns 防抖后的函数
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: number | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param limit 限制时间（毫秒）
 * @returns 节流后的函数
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle = false
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 验证URL格式
 * @param url URL字符串
 * @returns 是否为有效URL
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证版本号格式
 * @param version 版本号字符串
 * @returns 是否为有效版本号
 */
export const isValidVersion = (version: string): boolean => {
  return /^\d+\.\d+\.\d+$/.test(version)
}

/**
 * 比较版本号
 * @param version1 版本号1
 * @param version2 版本号2
 * @returns 比较结果：-1(小于), 0(等于), 1(大于)
 */
export const compareVersions = (version1: string, version2: string): number => {
  const v1Parts = version1.split('.').map(Number)
  const v2Parts = version2.split('.').map(Number)
  
  for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
    const v1Part = v1Parts[i] || 0
    const v2Part = v2Parts[i] || 0
    
    if (v1Part < v2Part) return -1
    if (v1Part > v2Part) return 1
  }
  
  return 0
}