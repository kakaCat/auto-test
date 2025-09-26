/**
 * 表单验证组合式函数
 */

import { ref, reactive } from 'vue'
import type { Ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

import type { SystemFormData, ModuleFormData } from '../types'
import { systemFormRules, moduleFormRules, isValidUrl, isValidVersion } from '../data/index'

export interface UseFormValidationReturn {
  systemFormRef: Ref<FormInstance | undefined>
  moduleFormRef: Ref<FormInstance | undefined>
  systemRules: FormRules
  moduleRules: FormRules
  validateSystemForm: () => Promise<boolean>
  validateModuleForm: () => Promise<boolean>
  resetSystemValidation: () => void
  resetModuleValidation: () => void
  validateField: (formRef: Ref<FormInstance | undefined>, field: string) => Promise<boolean>
  clearValidation: (formRef: Ref<FormInstance | undefined>) => void
}

export const useFormValidation = (): UseFormValidationReturn => {
  // 表单引用
  const systemFormRef = ref<FormInstance>()
  const moduleFormRef = ref<FormInstance>()
  
  // 自定义验证规则
  const validateUrl = (rule: any, value: string, callback: Function) => {
    if (value && !isValidUrl(value)) {
      callback(new Error('请输入有效的URL地址'))
    } else {
      callback()
    }
  }
  
  const validateVersion = (rule: any, value: string, callback: Function) => {
    if (value && !isValidVersion(value)) {
      callback(new Error('版本号格式应为 x.y.z'))
    } else {
      callback()
    }
  }
  
  const validatePath = (rule: any, value: string, callback: Function) => {
    if (value && !value.startsWith('/')) {
      callback(new Error('路径必须以 / 开头'))
    } else {
      callback()
    }
  }
  
  const validateTags = (rule: any, value: string[], callback: Function) => {
    if (value && value.length === 0) {
      callback(new Error('至少选择一个标签'))
    } else {
      callback()
    }
  }
  
  // 扩展的表单验证规则
  const systemRules: FormRules = {
    ...systemFormRules,
    url: [
      { required: false, message: '请输入系统访问地址', trigger: 'blur' },
      { validator: validateUrl, trigger: 'blur' }
    ]
  }
  
  const moduleRules: FormRules = {
    ...moduleFormRules,
    path: [
      { required: true, message: '请输入模块路径', trigger: 'blur' },
      { validator: validatePath, trigger: 'blur' }
    ],
    version: [
      { required: true, message: '请输入版本号', trigger: 'blur' },
      { validator: validateVersion, trigger: 'blur' }
    ],
    tags: [
      { required: true, message: '请选择标签', trigger: 'change' },
      { validator: validateTags, trigger: 'change' }
    ]
  }
  
  // 验证系统表单
  const validateSystemForm = async (): Promise<boolean> => {
    if (!systemFormRef.value) {
      ElMessage.error('表单引用未找到')
      return false
    }
    
    try {
      await systemFormRef.value.validate()
      return true
    } catch (error) {
      console.error('系统表单验证失败:', error)
      ElMessage.error('请检查表单输入')
      return false
    }
  }
  
  // 验证模块表单
  const validateModuleForm = async (): Promise<boolean> => {
    if (!moduleFormRef.value) {
      ElMessage.error('表单引用未找到')
      return false
    }
    
    try {
      await moduleFormRef.value.validate()
      return true
    } catch (error) {
      console.error('模块表单验证失败:', error)
      ElMessage.error('请检查表单输入')
      return false
    }
  }
  
  // 重置系统表单验证
  const resetSystemValidation = (): void => {
    if (systemFormRef.value) {
      systemFormRef.value.resetFields()
      systemFormRef.value.clearValidate()
    }
  }
  
  // 重置模块表单验证
  const resetModuleValidation = (): void => {
    if (moduleFormRef.value) {
      moduleFormRef.value.resetFields()
      moduleFormRef.value.clearValidate()
    }
  }
  
  // 验证单个字段
  const validateField = async (
    formRef: Ref<FormInstance | undefined>, 
    field: string
  ): Promise<boolean> => {
    if (!formRef.value) {
      return false
    }
    
    try {
      await formRef.value.validateField(field)
      return true
    } catch (error) {
      console.error(`字段 ${field} 验证失败:`, error)
      return false
    }
  }
  
  // 清除验证
  const clearValidation = (formRef: Ref<FormInstance | undefined>): void => {
    if (formRef.value) {
      formRef.value.clearValidate()
    }
  }
  
  return {
    systemFormRef,
    moduleFormRef,
    systemRules,
    moduleRules,
    validateSystemForm,
    validateModuleForm,
    resetSystemValidation,
    resetModuleValidation,
    validateField,
    clearValidation
  }
}