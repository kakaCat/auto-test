import { describe, it, expect, vi } from 'vitest'

// 先 mock 提示组件，确保断言可用
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

describe('ApiTestScenarioDrawer 创建流程', () => {
  it('成功创建后重置表单并刷新列表', async () => {
    const createSpy = vi.spyOn(scenarioApi, 'create').mockResolvedValue({ data: { id: 'S1' } })
    const getListSpy = vi.spyOn(scenarioApi, 'getList').mockResolvedValue({ data: [] })

    const wrapper = mount(ApiTestScenarioDrawer, {
      props: { visible: true, apiInfo: { id: 11, name: 'API-Create' } },
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

    // 填充创建表单
    wrapper.vm.createForm.name = '新场景'
    wrapper.vm.createForm.description = '描述'
    wrapper.vm.createForm.scenario_type = 'exception'

    // 触发创建
    await wrapper.vm.handleCreate()

    // 校验请求 payload
    expect(createSpy).toHaveBeenCalled()
    const payload = createSpy.mock.calls[0][0]
    expect(payload).toEqual({
      name: '新场景',
      description: '描述',
      scenario_type: 'exception',
      api_id: '11'
    })

    // 成功提示、表单重置、刷新列表
    expect(ElMessage.success).toHaveBeenCalled()
    expect(wrapper.vm.createForm.name).toBe('')
    expect(wrapper.vm.createForm.description).toBe('')
    expect(wrapper.vm.createForm.scenario_type).toBe('normal')
    expect(getListSpy).toHaveBeenCalled()
  })
})