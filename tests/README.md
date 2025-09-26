# 测试文件目录

本目录包含项目的测试文件和调试工具。

## 文件说明

### 🧪 测试脚本
- **test_frontend_api.js** - 前端API测试脚本
  - 测试前端API调用功能
  - 验证API响应格式
  - 用于自动化测试

### 🔧 调试工具
- **debug_api_management.html** - API管理调试页面
  - 可视化API调试界面
  - 测试系统列表和模块列表API
  - 重现和分析API错误
  - 在浏览器中打开即可使用

- **debug_404_errors.html** - 404错误调试工具
  - 监控网络请求和404错误
  - 自动捕获和记录错误信息
  - 测试API端点可用性
  - 检查资源路径问题

- **test_add_api_function.html** - 新增API功能测试页面
  - 专门测试新增API功能
  - 提供测试步骤指导
  - 快速检查功能状态
  - 问题排查建议

## 使用方法

### 运行API测试脚本
```bash
# 确保后端服务运行在 localhost:8001
node test_frontend_api.js
```

### 使用API调试页面
1. 确保后端服务运行在 localhost:8001
2. 在浏览器中打开 `debug_api_management.html`
3. 点击相应按钮测试API功能

## 注意事项

- 运行测试前请确保后端服务已启动
- 调试工具主要用于开发和问题排查
- 测试文件可以根据需要进行修改和扩展