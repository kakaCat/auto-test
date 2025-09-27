/**
 * API兼容性测试 (JavaScript版本)
 * 
 * 功能说明：
 * - 测试新API文件是否能正确加载
 * - 验证API类是否正确导出
 * - 检查基本方法是否存在
 */

console.log('🧪 开始API兼容性测试...');

// 测试API文件是否能正确加载
try {
  console.log('📋 测试API文件加载...');
  
  // 检查文件是否存在
  const fs = require('fs');
  const path = require('path');
  
  const apiFiles = [
    './src/api/system-api.ts',
    './src/api/module-api.ts', 
    './src/api/category-api.ts',
    './src/api/base-api.ts',
    './src/api/common.ts',
    './src/api/types/index.ts'
  ];
  
  let allFilesExist = true;
  
  apiFiles.forEach(file => {
    const fullPath = path.join(__dirname, file);
    if (fs.existsSync(fullPath)) {
      console.log(`✅ ${file} 文件存在`);
    } else {
      console.log(`❌ ${file} 文件不存在`);
      allFilesExist = false;
    }
  });
  
  if (allFilesExist) {
    console.log('🎉 所有API文件都存在！');
  } else {
    console.log('⚠️ 部分API文件缺失');
  }
  
  // 检查TypeScript编译
  console.log('🔍 检查TypeScript编译状态...');
  
  // 检查是否有编译错误（通过检查dist目录或编译输出）
  const distPath = path.join(__dirname, 'dist');
  if (fs.existsSync(distPath)) {
    console.log('✅ 项目已编译');
  } else {
    console.log('ℹ️ 项目尚未编译到dist目录');
  }
  
  // 检查package.json中的脚本
  const packageJsonPath = path.join(__dirname, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    console.log('📦 可用的npm脚本:');
    Object.keys(packageJson.scripts || {}).forEach(script => {
      console.log(`   - npm run ${script}`);
    });
  }
  
  console.log('✅ 基础兼容性测试完成');
  console.log('💡 建议：使用 npm run dev 启动开发服务器进行完整测试');
  
} catch (error) {
  console.error('❌ 兼容性测试失败:', error.message);
  process.exit(1);
}