/**
 * API兼容性测试
 * 
 * 功能说明：
 * - 测试新API与现有代码的兼容性
 * - 验证API调用是否正常工作
 * - 确保不会破坏现有功能
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

import { systemApi } from './system-api';
import { moduleApi } from './module-api';
import { categoryApi } from './category-api';

/**
 * 测试系统API兼容性
 */
export async function testSystemApiCompatibility() {
  console.log('🧪 开始测试系统API兼容性...');
  
  try {
    // 测试获取系统列表
    console.log('📋 测试获取系统列表...');
    const systemListResult = await systemApi.getList({ page: 1, pageSize: 10 });
    console.log('✅ 系统列表获取成功:', systemListResult);
    
    // 测试获取启用的系统
    console.log('🔍 测试获取启用的系统...');
    const enabledSystemsResult = await systemApi.getEnabledSystems();
    console.log('✅ 启用系统获取成功:', enabledSystemsResult);
    
    // 测试获取系统统计
    console.log('📊 测试获取系统统计...');
    const statsResult = await systemApi.getStatistics();
    console.log('✅ 系统统计获取成功:', statsResult);
    
    return { success: true, message: '系统API兼容性测试通过' };
  } catch (error: any) {
    console.error('❌ 系统API兼容性测试失败:', error);
    return { success: false, message: `系统API测试失败: ${error?.message || error}` };
  }
}

/**
 * 测试模块API兼容性
 */
export async function testModuleApiCompatibility() {
  console.log('🧪 开始测试模块API兼容性...');
  
  try {
    // 测试获取模块列表
    console.log('📋 测试获取模块列表...');
    const moduleListResult = await moduleApi.getList({ page: 1, pageSize: 10 });
    console.log('✅ 模块列表获取成功:', moduleListResult);
    
    // 测试获取启用的模块
    console.log('🔍 测试获取启用的模块...');
    const enabledModulesResult = await moduleApi.getEnabledModules();
    console.log('✅ 启用模块获取成功:', enabledModulesResult);
    
    // 测试按标签获取模块（如果有标签的话）
    console.log('🏷️ 测试按标签获取模块...');
    const taggedModulesResult = await moduleApi.getByTags(['test']);
    console.log('✅ 按标签获取模块成功:', taggedModulesResult);
    
    return { success: true, message: '模块API兼容性测试通过' };
  } catch (error: any) {
    console.error('❌ 模块API兼容性测试失败:', error);
    return { success: false, message: `模块API测试失败: ${error?.message || error}` };
  }
}

/**
 * 测试分类API兼容性
 */
export async function testCategoryApiCompatibility() {
  console.log('🧪 开始测试分类API兼容性...');
  
  try {
    // 测试获取分类列表
    console.log('📋 测试获取分类列表...');
    const categoryListResult = await categoryApi.getList({ page: 1, pageSize: 10 });
    console.log('✅ 分类列表获取成功:', categoryListResult);
    
    // 测试获取树形分类结构
    console.log('🌳 测试获取树形分类结构...');
    const treeResult = await categoryApi.getTree();
    console.log('✅ 分类树获取成功:', treeResult);
    
    // 测试获取根分类
    console.log('🌱 测试获取根分类...');
    const rootCategoriesResult = await categoryApi.getRootCategories();
    console.log('✅ 根分类获取成功:', rootCategoriesResult);
    
    return { success: true, message: '分类API兼容性测试测试通过' };
  } catch (error: any) {
    console.error('❌ 分类API兼容性测试失败:', error);
    return { success: false, message: `分类API测试失败: ${error?.message || error}` };
  }
}

/**
 * 运行所有兼容性测试
 */
export async function runAllCompatibilityTests() {
  console.log('🚀 开始运行所有API兼容性测试...');
  
  const results = [];
  
  // 测试系统API
  const systemResult = await testSystemApiCompatibility();
  results.push({ api: 'System API', ...systemResult });
  
  // 测试模块API
  const moduleResult = await testModuleApiCompatibility();
  results.push({ api: 'Module API', ...moduleResult });
  
  // 测试分类API
  const categoryResult = await testCategoryApiCompatibility();
  results.push({ api: 'Category API', ...categoryResult });
  
  // 汇总结果
  const successCount = results.filter(r => r.success).length;
  const totalCount = results.length;
  
  console.log('📊 兼容性测试结果汇总:');
  results.forEach(result => {
    const status = result.success ? '✅' : '❌';
    console.log(`${status} ${result.api}: ${result.message}`);
  });
  
  const overallSuccess = successCount === totalCount;
  const summary = `${successCount}/${totalCount} 个API测试通过`;
  
  console.log(overallSuccess ? '🎉' : '⚠️', '总体结果:', summary);
  
  return {
    success: overallSuccess,
    summary,
    results,
    successCount,
    totalCount
  };
}

/**
 * 测试旧版API兼容性（别名方法）
 */
export async function testLegacyApiCompatibility() {
  console.log('🧪 开始测试旧版API兼容性...');
  
  try {
    // 测试模块API的旧版方法
    console.log('📋 测试旧版模块API方法...');
    
    // 这些方法应该会显示废弃警告但仍然工作
    const legacyModulesBySystem = await moduleApi.getModulesBySystem('test-system-id');
    console.log('✅ 旧版getModulesBySystem方法工作正常');
    
    // 测试分类API的旧版方法
    console.log('🌳 测试旧版分类API方法...');
    const legacyCategoryTree = await categoryApi.getCategoryTree();
    console.log('✅ 旧版getCategoryTree方法工作正常');
    
    return { success: true, message: '旧版API兼容性测试通过' };
  } catch (error: any) {
    console.error('❌ 旧版API兼容性测试失败:', error);
    return { success: false, message: `旧版API测试失败: ${error?.message || error}` };
  }
}

// 导出测试函数
export default {
  testSystemApiCompatibility,
  testModuleApiCompatibility,
  testCategoryApiCompatibility,
  runAllCompatibilityTests,
  testLegacyApiCompatibility
};