# 前端代码注释规范

## 1. 总体原则

### 1.1 注释目的
- **业务逻辑说明**：解释代码的业务含义和目的
- **复杂逻辑解释**：对复杂算法、数据处理逻辑进行详细说明
- **接口文档化**：为组件、函数、API调用提供清晰的文档
- **维护便利性**：帮助团队成员快速理解和维护代码

### 1.2 注释语言
- 统一使用中文注释
- 专业术语可保留英文，但需要中文解释
- 注释内容要准确、简洁、易懂

## 2. 文件级注释

### 2.1 文件头注释
每个文件都应包含文件头注释，说明文件的用途、作者、创建时间等信息：

```javascript
/**
 * @fileoverview 用户管理页面组件
 * @description 提供用户列表展示、添加、编辑、删除等功能
 * @author 开发团队
 * @created 2024-01-01
 * @updated 2024-01-15
 */
```

### 2.2 Vue组件文件注释
```vue
<!--
/**
 * @component UserManagement
 * @description 用户管理主页面组件
 * @features
 *   - 用户列表展示（分页、搜索、筛选）
 *   - 用户信息的增删改查
 *   - 用户权限管理
 *   - 批量操作功能
 * @dependencies
 *   - Element Plus UI组件库
 *   - Pinia状态管理
 *   - Vue Router路由
 */
-->
```

## 3. 函数/方法注释

### 3.1 JSDoc标准注释
使用JSDoc标准为函数提供详细文档：

```javascript
/**
 * 获取用户列表数据
 * @description 从后端API获取用户列表，支持分页、搜索和筛选
 * @param {Object} params - 查询参数对象
 * @param {number} params.page - 页码，从1开始
 * @param {number} params.pageSize - 每页数量，默认20
 * @param {string} [params.keyword] - 搜索关键词，可选
 * @param {string} [params.status] - 用户状态筛选，可选
 * @returns {Promise<Object>} 返回用户列表数据
 * @returns {Array} returns.data - 用户数据数组
 * @returns {number} returns.total - 总记录数
 * @returns {number} returns.page - 当前页码
 * @throws {Error} 当网络请求失败时抛出错误
 * @example
 * const result = await getUserList({
 *   page: 1,
 *   pageSize: 20,
 *   keyword: '张三'
 * });
 */
async function getUserList(params) {
  // 实现代码...
}
```

### 3.2 Vue组合式API注释
```javascript
/**
 * 用户管理相关的组合式函数
 * @description 封装用户数据获取、状态管理和操作方法
 * @returns {Object} 返回用户管理相关的响应式数据和方法
 * @returns {Ref<Array>} returns.userList - 用户列表响应式数据
 * @returns {Ref<boolean>} returns.loading - 加载状态
 * @returns {Function} returns.fetchUsers - 获取用户列表方法
 * @returns {Function} returns.deleteUser - 删除用户方法
 */
function useUserManagement() {
  // 实现代码...
}
```

## 4. 组件注释

### 4.1 Props注释
```javascript
/**
 * 组件属性定义
 */
const props = defineProps({
  /**
   * 用户ID
   * @type {number|string}
   * @required
   * @description 用户的唯一标识符，用于获取用户详细信息
   */
  userId: {
    type: [Number, String],
    required: true
  },
  
  /**
   * 显示模式
   * @type {string}
   * @default 'view'
   * @description 组件显示模式：'view'查看模式，'edit'编辑模式
   */
  mode: {
    type: String,
    default: 'view',
    validator: (value) => ['view', 'edit'].includes(value)
  }
});
```

### 4.2 Emits注释
```javascript
/**
 * 组件事件定义
 */
const emit = defineEmits({
  /**
   * 用户信息更新事件
   * @param {Object} user - 更新后的用户信息对象
   * @description 当用户信息被成功更新时触发此事件
   */
  'user-updated': (user) => user && typeof user === 'object',
  
  /**
   * 取消操作事件
   * @description 当用户点击取消按钮时触发
   */
  'cancel': null
});
```

## 5. 业务逻辑注释

### 5.1 复杂业务逻辑
```javascript
// 用户权限验证逻辑
// 1. 检查用户是否已登录
// 2. 验证用户角色权限
// 3. 检查特定功能权限
if (userStore.isLoggedIn) {
  // 已登录用户，检查角色权限
  const hasPermission = userStore.hasRole(['admin', 'manager']);
  
  if (hasPermission) {
    // 有权限的用户可以执行操作
    await executeUserOperation();
  } else {
    // 权限不足，显示提示信息
    ElMessage.warning('您没有执行此操作的权限');
  }
} else {
  // 未登录用户，跳转到登录页
  router.push('/login');
}
```

### 5.2 数据处理逻辑
```javascript
/**
 * 处理用户列表数据
 * @description 对从API获取的原始用户数据进行格式化和增强
 */
const processUserData = (rawData) => {
  return rawData.map(user => {
    // 格式化用户状态显示文本
    const statusText = user.status === 1 ? '启用' : '禁用';
    
    // 计算用户年龄（基于生日）
    const age = user.birthday ? 
      new Date().getFullYear() - new Date(user.birthday).getFullYear() : 
      null;
    
    // 格式化最后登录时间
    const lastLoginText = user.last_login ? 
      formatDateTime(user.last_login) : 
      '从未登录';
    
    return {
      ...user,
      statusText,
      age,
      lastLoginText
    };
  });
};
```

## 6. API调用注释

### 6.1 API接口注释
```javascript
/**
 * 用户管理API接口
 */
export const userApi = {
  /**
   * 获取用户列表
   * @api GET /api/users
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.pageSize - 每页数量
   * @param {string} [params.keyword] - 搜索关键词
   * @returns {Promise<ApiResponse>} API响应数据
   */
  getUsers: (params) => request.get('/api/users', { params }),
  
  /**
   * 创建新用户
   * @api POST /api/users
   * @param {Object} userData - 用户数据对象
   * @param {string} userData.name - 用户姓名
   * @param {string} userData.email - 用户邮箱
   * @param {string} userData.phone - 用户手机号
   * @returns {Promise<ApiResponse>} 创建结果
   */
  createUser: (userData) => request.post('/api/users', userData)
};
```

## 7. 状态管理注释

### 7.1 Pinia Store注释
```javascript
/**
 * 用户状态管理Store
 * @description 管理用户相关的全局状态，包括用户信息、权限、偏好设置等
 */
export const useUserStore = defineStore('user', () => {
  // 状态定义
  /**
   * 当前登录用户信息
   * @type {Ref<Object|null>}
   */
  const currentUser = ref(null);
  
  /**
   * 用户权限列表
   * @type {Ref<Array>}
   */
  const permissions = ref([]);
  
  // Getters
  /**
   * 检查用户是否已登录
   * @returns {boolean} 登录状态
   */
  const isLoggedIn = computed(() => !!currentUser.value);
  
  // Actions
  /**
   * 用户登录
   * @param {Object} credentials - 登录凭据
   * @param {string} credentials.username - 用户名
   * @param {string} credentials.password - 密码
   * @returns {Promise<boolean>} 登录是否成功
   */
  const login = async (credentials) => {
    // 登录逻辑实现...
  };
  
  return {
    currentUser,
    permissions,
    isLoggedIn,
    login
  };
});
```

## 8. 样式注释

### 8.1 CSS/SCSS注释
```scss
/* 用户管理页面样式 */
.user-management {
  /* 页面容器样式 */
  padding: 20px;
  background-color: #f5f5f5;
  
  /* 搜索区域样式 */
  .search-section {
    margin-bottom: 20px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    
    /* 搜索表单布局 */
    .search-form {
      display: flex;
      gap: 16px;
      align-items: center;
      flex-wrap: wrap;
    }
  }
  
  /* 用户列表表格样式 */
  .user-table {
    background: white;
    border-radius: 8px;
    
    /* 表格头部样式 */
    .table-header {
      padding: 16px;
      border-bottom: 1px solid #ebeef5;
      
      /* 操作按钮组 */
      .action-buttons {
        display: flex;
        gap: 8px;
      }
    }
  }
}
```

## 9. 配置文件注释

### 9.1 路由配置注释
```javascript
/**
 * 用户管理模块路由配置
 * @description 定义用户管理相关页面的路由规则
 */
export const userRoutes = [
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('@/views/user-management/index.vue'),
    meta: {
      title: '用户管理',
      requiresAuth: true, // 需要登录
      permissions: ['user:view'], // 需要的权限
      breadcrumb: ['首页', '用户管理'] // 面包屑导航
    }
  }
];
```

## 10. 注释维护规范

### 10.1 注释更新原则
- 代码修改时必须同步更新相关注释
- 删除无用代码时要删除对应注释
- 重构代码时要重新审查注释的准确性

### 10.2 注释审查要点
- 注释是否准确反映代码功能
- 注释是否有助于理解业务逻辑
- 注释格式是否符合规范
- 注释内容是否简洁明了

## 11. 工具和插件推荐

### 11.1 VSCode插件
- **Document This**: 自动生成JSDoc注释
- **Better Comments**: 增强注释显示效果
- **Todo Highlight**: 高亮TODO注释

### 11.2 ESLint规则
```javascript
// .eslintrc.js 中的注释相关规则
rules: {
  'valid-jsdoc': 'warn', // 验证JSDoc注释格式
  'require-jsdoc': ['warn', {
    require: {
      FunctionDeclaration: true,
      MethodDefinition: true,
      ClassDeclaration: true
    }
  }]
}
```

这个注释规范将帮助团队编写高质量、易维护的前端代码，提高开发效率和代码可读性。