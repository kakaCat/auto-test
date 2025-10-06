import { describe, it, expect, vi } from 'vitest'

// 先 mock 提示组件，捕获错误提示
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

import { mount } from '@vue/test-utils'
import ApiTestScenarioDrawer from '@/views/api-management/components/ApiTestScenarioDrawer.vue'
import { scenarioApi } from '@/api/unified-api'
import { ElMessage } from 'element-plus'

describe('ApiTestScenarioDrawer 错误分支', () => {
  it('加载场景失败时提示错误并关闭 loading', async () => {
    const getListSpy = vi.spyOn(scenarioApi, 'getList').mockRejectedValue(new Error('网络错误'))

    const wrapper = mount(ApiTestScenarioDrawer, {
      props: { visible: true, apiInfo: { id: 99, name: 'API-Err' } },
      global: {
        stubs: {
          'SavedParametersList': true,
          'ParameterSaveDialog': true,
          'el-card': { template: '<div class="el-card"><slot name="header"></slot><slot /></div>' },
          'el-table': { template: '<div class="el-table"><slot /></div>' },
          'el-table-column': true,
          'el-input': true,
          'el-select': true,
          'el-checkbox': true,
          'el-button': true,
          'el-tag': true,
          'el-icon': true,
          'el-drawer': { template: '<div class="el-drawer"><slot /></div>' }
        }
      }
    })

    await wrapper.vm.loadScenarios()
    expect(getListSpy).toHaveBeenCalled()
    expect(ElMessage.error).toHaveBeenCalled()
    expect(wrapper.vm.loading).toBe(false)
  })

  it('创建失败时提示错误且不清空表单', async () => {
    vi.spyOn(scenarioApi, 'create').mockRejectedValue(new Error('创建失败'))

    const wrapper = mount(ApiTestScenarioDrawer, {
      props: { visible: true, apiInfo: { id: 100, name: 'API-Err2' } },
      global: {
        stubs: {
          'SavedParametersList': true,
          'ParameterSaveDialog': true,
          'el-card': { template: '<div class="el-card"><slot name="header"></slot><slot /></div>' },
          'el-table': { template: '<div class="el-table"><slot /></div>' },
          'el-table-column': true,
          'el-input': true,
          'el-select': true,
          'el-checkbox': true,
          'el-button': true,
          'el-tag': true,
          'el-icon': true,
          'el-form': { template: '<form><slot /></form>' },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-drawer': { template: '<div class="el-drawer"><slot /></div>' }
        }
      }
    })

    // 设置表单并触发创建
    wrapper.vm.createForm.name = '保留名称'
    wrapper.vm.createForm.description = '保留描述'
    wrapper.vm.createForm.scenario_type = 'boundary'
    await wrapper.vm.handleCreate()

    // 错误提示且保留原值
    expect(ElMessage.error).toHaveBeenCalled()
    expect(wrapper.vm.createForm.name).toBe('保留名称')
    expect(wrapper.vm.createForm.description).toBe('保留描述')
    expect(wrapper.vm.createForm.scenario_type).toBe('boundary')
  })
})