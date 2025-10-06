import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ApiTestScenarioDrawer from '@/views/api-management/components/ApiTestScenarioDrawer.vue'
import { scenarioApi } from '@/api/unified-api'

describe('ApiTestScenarioDrawer 筛选参数与请求', () => {
  it('根据 filters 构造 getList 请求参数并包含必填 api_id', async () => {
    const getListSpy = vi.spyOn(scenarioApi, 'getList').mockResolvedValue({ data: [] })

    const wrapper = mount(ApiTestScenarioDrawer, {
      props: { visible: true, apiInfo: { id: 321, name: 'API X' } },
      global: {
        stubs: {
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

    // 设置筛选条件并手动触发加载
    wrapper.vm.filters.keyword = 'foo'
    wrapper.vm.filters.status = 'active'
    wrapper.vm.filters.is_parameters_saved = true
    await wrapper.vm.loadScenarios()

    expect(getListSpy).toHaveBeenCalled()
    const firstArg = getListSpy.mock.calls[0][0]
    expect(firstArg).toEqual({
      api_id: '321',
      keyword: 'foo',
      status: 'active',
      is_parameters_saved: true
    })

    // 重置筛选后应仅携带 api_id
    getListSpy.mockClear()
    wrapper.vm.resetFilters()
    // resetFilters 内部会再次调用 loadScenarios（无需显式等待 DOM）
    await Promise.resolve()

    const secondArg = getListSpy.mock.calls[0][0]
    expect(secondArg).toEqual({ api_id: '321' })
  })
})