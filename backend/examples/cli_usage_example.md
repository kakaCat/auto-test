# AI场景执行命令行工具使用示例

本文档展示如何使用命令行工具来执行AI场景调用的完整流程。

## 快速开始

### 1. 基本场景执行

```bash
# 执行场景1，用户描述为"注册新用户"
./scenario execute 1 "注册新用户，邮箱是 john@example.com，密码是 123456"

# 执行场景2，带初始参数
./scenario execute 2 "查询用户信息" --params '{"user_id": 123}'

# 执行场景3，显示详细信息
./scenario execute 3 "创建订单并支付" --verbose
```

### 2. 查询执行状态

```bash
# 查询特定执行的状态
./scenario status exec_20241201_143022_1

# 以JSON格式显示状态
./scenario status exec_20241201_143022_1 --format json
```

### 3. 查看执行历史

```bash
# 查看最近10条执行历史
./scenario history

# 查看最近20条执行历史
./scenario history --limit 20

# 以JSON格式显示历史
./scenario history --format json
```

### 4. 查看代理状态

```bash
# 查看AI代理当前状态
./scenario agent-status

# 显示详细的代理状态信息
./scenario agent-status --verbose
```

### 5. 取消执行

```bash
# 取消当前正在执行的任务
./scenario cancel exec_20241201_143022_1
```

## 完整使用流程示例

### 场景1：用户注册流程

```bash
# 1. 执行用户注册场景
./scenario execute 1 "注册新用户，邮箱是 alice@example.com，用户名是 alice，密码是 password123"

# 输出示例：
# 🚀 开始执行场景 1...
# 📝 用户描述: 注册新用户，邮箱是 alice@example.com，用户名是 alice，密码是 password123
# 
# ==================================================
# 
# 📊 执行结果摘要
# ==================================================
# 状态: ✅ completed
# 执行ID: exec_20241201_143022_1
# 场景ID: 1
# 成功步骤: 3
# 失败步骤: 0
# 总执行时间: 2.45秒
# 
# 📋 执行步骤
# ------------------------------
# 1. ✅ 验证邮箱格式 (API 101)
#    状态: success
#    执行时间: 0.12秒
# 
# 2. ✅ 检查用户名可用性 (API 102)
#    状态: success
#    执行时间: 0.89秒
# 
# 3. ✅ 创建用户账户 (API 103)
#    状态: success
#    执行时间: 1.44秒

# 2. 查询刚才的执行状态
./scenario status exec_20241201_143022_1
```

### 场景2：电商购物流程

```bash
# 1. 执行购物场景，带初始参数
./scenario execute 5 "用户购买商品" --params '{
  "user_id": 123,
  "product_id": 456,
  "quantity": 2,
  "payment_method": "credit_card"
}' --verbose

# 输出示例：
# 🚀 开始执行场景 5...
# 📝 用户描述: 用户购买商品
# ⚙️  初始参数: {"user_id": 123, "product_id": 456, "quantity": 2, "payment_method": "credit_card"}
# 
# ==================================================
# 
# 📊 执行结果摘要
# ==================================================
# 状态: ✅ completed
# 执行ID: exec_20241201_143155_5
# 场景ID: 5
# 成功步骤: 5
# 失败步骤: 0
# 总执行时间: 4.23秒
# 
# 🔧 参数增强结果
# ------------------------------
#   user_id: 123
#   product_id: 456
#   quantity: 2
#   payment_method: credit_card
#   order_id: ORD_20241201_143155
#   total_amount: 299.98
#   shipping_address: 用户默认地址
# 
# 📋 执行步骤
# ------------------------------
# 1. ✅ 验证用户身份 (API 201)
#    状态: success
#    执行时间: 0.45秒
#    输入参数: {"user_id": 123}
#    输出结果: {"valid": true, "user_name": "Alice"}
# 
# 2. ✅ 检查商品库存 (API 202)
#    状态: success
#    执行时间: 0.67秒
#    输入参数: {"product_id": 456, "quantity": 2}
#    输出结果: {"available": true, "stock": 50, "price": 149.99}
# 
# 3. ✅ 创建订单 (API 203)
#    状态: success
#    执行时间: 1.23秒
#    输入参数: {"user_id": 123, "product_id": 456, "quantity": 2, "total_amount": 299.98}
#    输出结果: {"order_id": "ORD_20241201_143155", "status": "created"}
# 
# 4. ✅ 处理支付 (API 204)
#    状态: success
#    执行时间: 1.56秒
#    输入参数: {"order_id": "ORD_20241201_143155", "payment_method": "credit_card", "amount": 299.98}
#    输出结果: {"payment_id": "PAY_20241201_143156", "status": "success"}
# 
# 5. ✅ 更新库存 (API 205)
#    状态: success
#    执行时间: 0.32秒
#    输入参数: {"product_id": 456, "quantity": 2}
#    输出结果: {"new_stock": 48, "updated": true}
```

### 场景3：处理执行失败的情况

```bash
# 1. 执行一个可能失败的场景
./scenario execute 8 "转账操作，从账户A转账1000元到账户B"

# 输出示例（失败情况）：
# 🚀 开始执行场景 8...
# 📝 用户描述: 转账操作，从账户A转账1000元到账户B
# 
# ==================================================
# 
# 📊 执行结果摘要
# ==================================================
# 状态: ❌ failed
# 执行ID: exec_20241201_144022_8
# 场景ID: 8
# 成功步骤: 2
# 失败步骤: 1
# 总执行时间: 1.89秒
# 错误摘要: 账户余额不足，无法完成转账
# 
# 📋 执行步骤
# ------------------------------
# 1. ✅ 验证源账户 (API 301)
#    状态: success
#    执行时间: 0.34秒
# 
# 2. ✅ 验证目标账户 (API 302)
#    状态: success
#    执行时间: 0.28秒
# 
# 3. ❌ 执行转账 (API 303)
#    状态: failed
#    执行时间: 1.27秒
#    错误: 账户余额不足，当前余额：500元，转账金额：1000元

# 2. 查看执行历史，了解最近的执行情况
./scenario history --limit 5

# 输出示例：
# 📚 执行历史 (最近 5 条)
# ================================================================================
# 序号 执行ID                    场景ID   状态         成功/失败   执行时间
# --------------------------------------------------------------------------------
# 1    exec_20241201_144022_8    8        failed       2/1        1.89s
# 2    exec_20241201_143155_5    5        completed    5/0        4.23s
# 3    exec_20241201_143022_1    1        completed    3/0        2.45s
# 4    exec_20241201_142845_3    3        partial_success 4/1     3.67s
# 5    exec_20241201_142234_2    2        completed    2/0        1.23s
```

## 高级用法

### 1. 使用配置文件

创建配置文件 `config.json`：

```json
{
  "agent": {
    "auto_enhance_parameters": true,
    "stop_on_first_failure": false,
    "enable_smart_recovery": true,
    "max_retry_attempts": 5,
    "timeout_seconds": 600
  },
  "output": {
    "format": "table",
    "show_details": true,
    "color_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file": "scenario_execution.log"
  }
}
```

使用配置文件：

```bash
# 使用自定义配置执行场景
./scenario --config config.json execute 1 "测试场景"

# 使用自定义数据库连接
./scenario --database-url "mysql://user:pass@localhost:3306/testdb" execute 1 "测试场景"
```

### 2. 调试模式

```bash
# 启用调试模式，显示详细的执行信息
./scenario --debug execute 1 "调试测试场景"

# 启用详细模式
./scenario --verbose execute 1 "详细测试场景"
```

### 3. 不同输出格式

```bash
# JSON格式输出
./scenario --format json execute 1 "JSON输出测试"

# 简单格式输出
./scenario --format simple execute 1 "简单输出测试"

# 表格格式输出（默认）
./scenario --format table execute 1 "表格输出测试"
```

## 实际业务场景示例

### 1. 用户管理场景

```bash
# 用户注册
./scenario execute 1 "注册新用户，邮箱：user@example.com，手机：13800138000"

# 用户登录
./scenario execute 2 "用户登录，邮箱：user@example.com，密码：password123"

# 修改用户信息
./scenario execute 3 "修改用户信息，用户ID：123，新手机号：13900139000"

# 用户注销
./scenario execute 4 "注销用户账户，用户ID：123"
```

### 2. 电商业务场景

```bash
# 商品管理
./scenario execute 10 "添加新商品，名称：iPhone 15，价格：5999，库存：100"

# 购物车操作
./scenario execute 11 "添加商品到购物车，用户ID：123，商品ID：456，数量：2"

# 下单流程
./scenario execute 12 "创建订单并支付，用户ID：123，支付方式：支付宝"

# 订单管理
./scenario execute 13 "查询订单状态，订单ID：ORD_20241201_001"
```

### 3. 金融业务场景

```bash
# 账户操作
./scenario execute 20 "开户，客户姓名：张三，身份证：123456789012345678"

# 转账操作
./scenario execute 21 "转账，源账户：6222001234567890，目标账户：6222009876543210，金额：1000"

# 查询余额
./scenario execute 22 "查询账户余额，账户号：6222001234567890"
```

## 错误处理和故障排除

### 1. 常见错误

```bash
# 场景不存在
./scenario execute 999 "不存在的场景"
# 错误：场景999不存在

# 参数格式错误
./scenario execute 1 "测试" --params '{invalid json}'
# 错误：参数格式错误: Expecting property name enclosed in double quotes

# 数据库连接失败
./scenario --database-url "mysql://wrong:wrong@localhost:3306/wrong" execute 1 "测试"
# 错误：代理初始化失败: 数据库连接失败
```

### 2. 调试技巧

```bash
# 使用调试模式查看详细错误信息
./scenario --debug execute 1 "调试场景"

# 查看代理状态，确认组件是否正常
./scenario agent-status --verbose

# 查看执行历史，分析失败模式
./scenario history --limit 20 --format json
```

## 性能优化建议

1. **批量操作**：对于大量相似的场景执行，考虑使用脚本批量调用
2. **参数预处理**：提前准备好复杂的参数，避免在命令行中输入过长的JSON
3. **配置优化**：根据实际需求调整超时时间和重试次数
4. **日志管理**：定期清理执行日志，避免占用过多磁盘空间

## 集成到CI/CD流程

```bash
#!/bin/bash
# 自动化测试脚本示例

set -e

echo "开始执行自动化场景测试..."

# 执行关键业务场景
scenarios=(1 2 3 5 8)

for scenario_id in "${scenarios[@]}"; do
    echo "执行场景 $scenario_id..."
    ./scenario execute $scenario_id "自动化测试场景 $scenario_id" --format json > "result_$scenario_id.json"
    
    # 检查执行结果
    if grep -q '"final_status": "completed"' "result_$scenario_id.json"; then
        echo "✅ 场景 $scenario_id 执行成功"
    else
        echo "❌ 场景 $scenario_id 执行失败"
        exit 1
    fi
done

echo "所有场景测试完成！"
```

这个命令行工具提供了完整的AI场景执行功能，支持用户通过简单的命令来完成复杂的业务流程自动化测试。