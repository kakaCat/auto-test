# API管理常见问题与解决方案

## API编辑保存状态管理问题

### 问题描述
在API编辑表单中，点击保存按钮后，保存状态（loading）一直显示，无法重置，导致用户无法进行后续操作。

### 根本原因
前端`ApiFormDialog`组件的保存状态管理存在缺陷：
- 子组件`ApiFormDialog`触发保存事件后，`saving`状态设置为`true`
- 父组件`api-management/index.vue`处理保存逻辑，但未通知子组件重置状态
- 导致无论保存成功或失败，`saving`状态都无法重置为`false`

### 解决方案
1. 修改子组件 (`ApiFormDialog.vue`)：
   ```javascript
   // 添加重置保存状态的方法
   const resetSavingState = () => {
     saving.value = false
   }
   
   // 使用 defineExpose 暴露方法给父组件
   defineExpose({
     resetSavingState
   })
   ```

2. 修改父组件 (`api-management/index.vue`)：
   ```javascript
   // 添加子组件引用
   const apiFormDialogRef = ref()
   
   // 在 saveApi 方法中调用子组件的重置方法
   const saveApi = async (formData) => {
     try {
       // ... 保存逻辑
       // 保存成功后重置状态
       apiFormDialogRef.value.resetSavingState()
     } catch (error) {
       // 保存失败后也要重置状态
       apiFormDialogRef.value.resetSavingState()
     }
   }
   ```

### 修复效果
- 保存成功或失败后，loading状态都能正确重置
- 用户可以正常进行多次编辑保存操作
- 提升了用户体验和界面响应性

## 其他常见问题

### 表单验证问题
- 问题: 表单提交时验证不通过但没有明确提示
- 解决: 确保所有验证规则都有对应的错误提示信息

### 网络请求超时
- 问题: API请求超时导致页面卡死
- 解决: 设置合理的请求超时时间和重试机制

## 规范：API 管理交互与请求层最佳实践（防重复提示与状态卡死）

为避免再次出现“双提示”和保存状态无法重置的问题，遵循以下统一规范：

- 请求层（传输层）规范：
  - 统一使用 <mcfile name="request.ts" path="/Users/mac/Documents/ai/auto-test/frontend/src/utils/request.ts"></mcfile> 作为唯一传输层。
  - 请求层不产生任何 UI 副作用：不触发 ElMessage、不绑定全局 Loading、不做业务数据适配。
  - 所有 CRUD 操作直接调用 request.get/post/put/patch/delete；错误通过 `throw new Error('具体消息')` 返回到页面层处理。

- 页面层操作反馈（单一提示）：
  - 成功提示由页面控制，只弹一次：在 await 成功后调用 `ElMessage.success('操作成功')` 或上下文更贴切的文案。
  - 失败提示由页面控制，只弹一次：`catch (error: unknown) { ElMessage.error((error as Error)?.message || '操作失败') }`。
  - 使用 `finally` 保证状态重置与清理逻辑始终执行（如按钮 disabled、loading 还原、关闭弹窗、刷新列表）。

- 组件状态管理（父子协作）：
  - 子组件（如 ApiFormDialog）在保存流程中暴露重置方法：
    - `defineExpose({ resetSavingState })`，内部实现将 `saving.value = false`。
  - 父组件在保存逻辑中使用 `try/catch/finally`：
    - 成功或失败后均调用 `apiFormDialogRef.value.resetSavingState()`；在 finally 中统一调用以避免遗漏。
    - 同步执行界面清理动作：关闭对话框、刷新列表、重置表单。

- API 层（域 API）规范：
  - 移除并禁止使用 `@/utils/apiHandler`，统一改用 `request.*`。
  - 在域 API 内可保留纯数据转换（Converter/normalize）但不得产生 UI 副作用。
  - 复杂对象使用 interface，避免 any；异步返回 `Promise<T>`，错误用 `throw new Error('具体消息')`。

- 验收清单（每次改动都要自检）：
  - 成功/失败提示每次操作最多出现一次（页面层发起）。
  - 保存/提交的 loading 状态在成功或失败后都能正确重置（父子组件协作）。
  - 传输层无任何 UI 副作用；所有界面反馈在页面层实现。
  - 端点路径显式包含 `/api/...` 或完整域名，避免隐式前缀导致请求异常。