/**
 * 统一API聚合导出 (Unified API Aggregator)
 * 对齐既有子域文件命名规范（*-api.ts），移除重复目录依赖。
 * 保持原路径与导入兼容：默认与命名导出均透传至既有实现。
 */

import systemApi from './system-api'
import moduleApi from './module-api'
import { apiManagementApi } from './api-management'
import { pageApi } from './page-management'
import { testApisApi } from './test-apis'
import { scenarioApi, categoryApi } from './scenario'
import { workflowApi } from './workflow'
import requirementApi, { requirementApi as namedRequirementApi } from './requirement-management'

export { systemApi, moduleApi, categoryApi, apiManagementApi, pageApi, scenarioApi, workflowApi, testApisApi }
export { namedRequirementApi as requirementApi }

// 兼容旧版命名导出（unified*Api 别名），避免历史代码报错
export {
  systemApi as unifiedSystemApi,
  moduleApi as unifiedModuleApi,
  categoryApi as unifiedCategoryApi,
  apiManagementApi as unifiedApiManagementApi,
  pageApi as unifiedPageApi,
  scenarioApi as unifiedScenarioApi,
  workflowApi as unifiedWorkflowApi,
  namedRequirementApi as unifiedRequirementApi,
  testApisApi as unifiedTestApisApi
}

const unified = {
  system: systemApi,
  module: moduleApi,
  category: categoryApi,
  page: pageApi,
  scenario: scenarioApi,
  workflow: workflowApi,
  requirement: namedRequirementApi,
  apiManagementApi,
  testApisApi
}

export default unified