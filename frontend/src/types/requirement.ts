/**
 * 需求管理相关类型定义
 * Requirement Management Types
 */

// 需求基本信息
export interface Requirement {
  id: string
  title: string
  type: RequirementType
  category: string
  priority: Priority
  status: RequirementStatus
  description: string
  businessValue?: string
  acceptanceCriteria: string[]
  estimatedEffort?: string
  targetRelease?: string
  assignee?: string
  stakeholders: string[]
  dependencies: string[]
  technicalRisk: number
  businessRisk: number
  riskDescription?: string
  projectId: string
  createdAt?: string
  updatedAt?: string
  createdBy?: string
  updatedBy?: string
}

// 需求类型
export type RequirementType = 'functional' | 'performance' | 'security' | 'technical'

// 优先级
export type Priority = 'critical' | 'high' | 'medium' | 'low'

// 需求状态
export type RequirementStatus = 'draft' | 'in_development' | 'in_testing' | 'completed' | 'cancelled'

// 项目信息
export interface Project {
  id: string
  name: string
  description?: string
  owner?: string
  status: ProjectStatus
  createdAt?: string
  updatedAt?: string
}

// 项目状态
export type ProjectStatus = 'active' | 'inactive' | 'archived'

// 需求树节点
export interface RequirementTreeNode {
  id: string
  name: string
  type: 'project' | 'epic' | 'feature' | 'requirement'
  priority?: Priority
  status?: RequirementStatus | ProjectStatus
  children?: RequirementTreeNode[]
  disabled?: boolean
  expanded?: boolean
}

// 测试场景关联
export interface ScenarioLink {
  scenarioId: string
  scenarioName: string
  coverageType: CoverageType
  coverageWeight: number
  priority: Priority
  testType: TestType
}

// 覆盖类型
export type CoverageType = 'happy_path' | 'error_handling' | 'boundary' | 'performance'

// 测试类型
export type TestType = 'functional' | 'performance' | 'security' | 'integration' | 'regression'

// 测试计划
export interface TestPlan {
  id: string
  name: string
  targetRelease: string
  startDate: string
  endDate: string
  description: string
  testEnvironment: TestEnvironment
  testTypes: TestType[]
  requirementsInScope: RequirementInPlan[]
  entryCriteria: string[]
  exitCriteria: string[]
  risks: Risk[]
  status: TestPlanStatus
  progress: number
  createdAt?: string
  updatedAt?: string
}

// 测试环境
export type TestEnvironment = 'dev' | 'test' | 'staging' | 'production'

// 测试计划状态
export type TestPlanStatus = 'draft' | 'active' | 'completed' | 'cancelled'

// 计划中的需求
export interface RequirementInPlan {
  id: string
  title: string
  priority: Priority
  estimatedEffort?: string
  assignee?: string
  testScenarios: string[]
}

// 风险信息
export interface Risk {
  description: string
  level: RiskLevel
  mitigation: string
}

// 风险等级
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

// 覆盖率分析
export interface CoverageAnalysis {
  overall: OverallCoverage
  details: RequirementCoverage[]
  categoryBreakdown: CategoryCoverage[]
  trendData: CoverageTrend[]
}

// 总体覆盖率
export interface OverallCoverage {
  totalRequirements: number
  coveredRequirements: number
  coveragePercentage: number
  targetCoverage: number
}

// 需求覆盖率详情
export interface RequirementCoverage {
  requirementId: string
  requirementName: string
  category: RequirementType
  priority: Priority
  scenarioCount: number
  coveragePercentage: number
  status: CoverageStatus
  scenarioBreakdown?: ScenarioBreakdown[]
  gaps?: CoverageGap[]
}

// 覆盖率状态
export type CoverageStatus = 'excellent' | 'good' | 'fair' | 'poor'

// 场景分解
export interface ScenarioBreakdown {
  scenarioId: string
  scenarioName: string
  coverageType: CoverageType
  weight: number
  executionStatus: ExecutionStatus
}

// 执行状态
export type ExecutionStatus = 'passed' | 'failed' | 'pending' | 'skipped'

// 覆盖率缺口
export interface CoverageGap {
  id: string
  description: string
  severity: 'low' | 'medium' | 'high'
  recommendation?: string
}

// 分类覆盖率
export interface CategoryCoverage {
  category: RequirementType
  total: number
  covered: number
  percentage: number
  status: CoverageStatus
}

// 覆盖率趋势
export interface CoverageTrend {
  date: string
  coveragePercentage: number
  totalRequirements: number
  coveredRequirements: number
}

// 执行统计
export interface ExecutionStats {
  passRate: number
  coverage: number
  executionCount: number
  lastExecutionDate?: string
}

// API请求参数类型
export interface RequirementListParams {
  page?: number
  pageSize?: number
  projectId?: string
  type?: RequirementType
  priority?: Priority
  status?: RequirementStatus
  keyword?: string
}

export interface CoverageAnalysisParams {
  startDate?: string
  endDate?: string
  projectId?: string
  category?: RequirementType
}

// API响应类型
export interface RequirementListResponse {
  data: Requirement[]
  total: number
  page: number
  pageSize: number
}

export interface RequirementDetailResponse {
  data: Requirement
}

export interface TestPlanListResponse {
  data: TestPlan[]
  total: number
}

export interface CoverageAnalysisResponse {
  data: CoverageAnalysis
}