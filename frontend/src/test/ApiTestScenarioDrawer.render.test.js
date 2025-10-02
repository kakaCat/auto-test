import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ApiTestScenarioDrawer from '@/views/api-management/components/ApiTestScenarioDrawer.vue'
import unifiedApi from '@/api/unified-api'
import { nextTick } from 'vue'

describe('ApiTestScenarioDrawer 渲染与行为', () => {
  it('应在可见且提供 apiInfo 时加载场景列表，且无分页组件', async () => {
    // Mock 场景列表与详情接口
    vi.spyOn(unifiedApi.scenario, 'getList').mockResolvedValue({
      data: [
        { name: '场景A', scenario_type: 'normal', status: 'active', tags: ['a', 'b'] },
        { name: '场景B', scenario_type: 'exception', status: 'inactive', tags: [] }
      ]
    })
    vi.spyOn(unifiedApi.scenario, 'getDetail').mockResolvedValue({
      data: { variables: { v1: 1 }, config: { c1: true } }
    })

    const wrapper = mount(ApiTestScenarioDrawer, {
      props: {
        visible: true,
        apiInfo: { id: 123, name: 'Demo API' }
      },
      global: {
        // 简化 Element Plus 组件渲染，避免作用域插槽在空数据时抛错
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

    // 等待加载
    await nextTick()
    // 让微任务队列执行，以保证列表赋值
    await Promise.resolve()

    // 基本渲染断言：标题与列表区域存在
    const pageText = wrapper.text()
    expect(pageText).toContain('场景列表')
    expect(pageText).toContain('新建场景')
    expect(wrapper.find('.el-table').exists()).toBe(true)

    // 无分页组件（抽屉内列表不分页）
    expect(wrapper.find('.el-pagination').exists()).toBe(false)
  })
})