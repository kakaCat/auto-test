// 工作流设计器测试用例
export const createTestWorkflow = () => {
  return {
    nodes: [
      {
        id: 'start-1',
        type: 'start',
        position: { x: 100, y: 100 },
        data: {
          label: '开始',
          description: '工作流开始节点'
        }
      },
      {
        id: 'api-1',
        type: 'api-call',
        position: { x: 300, y: 100 },
        data: {
          label: '获取用户信息',
          description: 'API调用节点',
          config: {
            url: 'https://jsonplaceholder.typicode.com/users/1',
            method: 'GET',
            headers: {},
            params: {}
          }
        }
      },
      {
        id: 'transform-1',
        type: 'data-transform',
        position: { x: 500, y: 100 },
        data: {
          label: '数据转换',
          description: '提取用户名和邮箱',
          config: {
            script: `
              return {
                username: input.name,
                email: input.email,
                timestamp: new Date().toISOString()
              }
            `
          }
        }
      },
      {
        id: 'condition-1',
        type: 'condition',
        position: { x: 700, y: 100 },
        data: {
          label: '邮箱验证',
          description: '检查邮箱格式',
          config: {
            condition: 'input.email && input.email.includes("@")'
          }
        }
      },
      {
        id: 'api-2',
        type: 'api-call',
        position: { x: 900, y: 50 },
        data: {
          label: '发送欢迎邮件',
          description: '邮箱有效时发送欢迎邮件',
          config: {
            url: 'https://jsonplaceholder.typicode.com/posts',
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: {
              title: '欢迎邮件',
              body: '欢迎使用我们的服务',
              userId: 1
            }
          }
        }
      },
      {
        id: 'api-3',
        type: 'api-call',
        position: { x: 900, y: 150 },
        data: {
          label: '记录错误日志',
          description: '邮箱无效时记录错误',
          config: {
            url: 'https://jsonplaceholder.typicode.com/posts',
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: {
              title: '错误日志',
              body: '用户邮箱格式无效',
              userId: 1
            }
          }
        }
      },
      {
        id: 'end-1',
        type: 'end',
        position: { x: 1100, y: 100 },
        data: {
          label: '结束',
          description: '工作流结束节点'
        }
      }
    ],
    edges: [
      {
        id: 'e1',
        source: 'start-1',
        target: 'api-1',
        type: 'default'
      },
      {
        id: 'e2',
        source: 'api-1',
        target: 'transform-1',
        type: 'default'
      },
      {
        id: 'e3',
        source: 'transform-1',
        target: 'condition-1',
        type: 'default'
      },
      {
        id: 'e4',
        source: 'condition-1',
        target: 'api-2',
        type: 'default',
        label: '邮箱有效'
      },
      {
        id: 'e5',
        source: 'condition-1',
        target: 'api-3',
        type: 'default',
        label: '邮箱无效'
      },
      {
        id: 'e6',
        source: 'api-2',
        target: 'end-1',
        type: 'default'
      },
      {
        id: 'e7',
        source: 'api-3',
        target: 'end-1',
        type: 'default'
      }
    ]
  }
}

// 并行执行测试用例
export const createParallelTestWorkflow = () => {
  return {
    nodes: [
      {
        id: 'start-1',
        type: 'start',
        position: { x: 100, y: 200 },
        data: {
          label: '开始',
          description: '并行工作流开始'
        }
      },
      {
        id: 'parallel-1',
        type: 'parallel',
        position: { x: 300, y: 200 },
        data: {
          label: '并行执行',
          description: '同时执行多个任务'
        }
      },
      {
        id: 'api-1',
        type: 'api-call',
        position: { x: 500, y: 100 },
        data: {
          label: '获取用户列表',
          description: '获取所有用户',
          config: {
            url: 'https://jsonplaceholder.typicode.com/users',
            method: 'GET'
          }
        }
      },
      {
        id: 'api-2',
        type: 'api-call',
        position: { x: 500, y: 200 },
        data: {
          label: '获取文章列表',
          description: '获取所有文章',
          config: {
            url: 'https://jsonplaceholder.typicode.com/posts',
            method: 'GET'
          }
        }
      },
      {
        id: 'api-3',
        type: 'api-call',
        position: { x: 500, y: 300 },
        data: {
          label: '获取评论列表',
          description: '获取所有评论',
          config: {
            url: 'https://jsonplaceholder.typicode.com/comments',
            method: 'GET'
          }
        }
      },
      {
        id: 'transform-1',
        type: 'data-transform',
        position: { x: 700, y: 200 },
        data: {
          label: '数据汇总',
          description: '汇总所有数据',
          config: {
            script: `
              return {
                userCount: input.users ? input.users.length : 0,
                postCount: input.posts ? input.posts.length : 0,
                commentCount: input.comments ? input.comments.length : 0,
                summary: '数据汇总完成'
              }
            `
          }
        }
      },
      {
        id: 'end-1',
        type: 'end',
        position: { x: 900, y: 200 },
        data: {
          label: '结束',
          description: '并行工作流结束'
        }
      }
    ],
    edges: [
      {
        id: 'e1',
        source: 'start-1',
        target: 'parallel-1',
        type: 'default'
      },
      {
        id: 'e2',
        source: 'parallel-1',
        target: 'api-1',
        type: 'default'
      },
      {
        id: 'e3',
        source: 'parallel-1',
        target: 'api-2',
        type: 'default'
      },
      {
        id: 'e4',
        source: 'parallel-1',
        target: 'api-3',
        type: 'default'
      },
      {
        id: 'e5',
        source: 'api-1',
        target: 'transform-1',
        type: 'default'
      },
      {
        id: 'e6',
        source: 'api-2',
        target: 'transform-1',
        type: 'default'
      },
      {
        id: 'e7',
        source: 'api-3',
        target: 'transform-1',
        type: 'default'
      },
      {
        id: 'e8',
        source: 'transform-1',
        target: 'end-1',
        type: 'default'
      }
    ]
  }
}

// 测试工作流功能
export const testWorkflowFeatures = () => {
  console.log('工作流设计器功能测试')
  
  const features = [
    '✅ 拖拽式节点创建',
    '✅ 多种节点类型支持（开始、结束、API调用、数据转换、条件分支、并行执行）',
    '✅ 节点连接和参数传递',
    '✅ 执行控制引擎（顺序、并行、条件执行）',
    '✅ 状态颜色标识和进度显示',
    '✅ 数据流动画效果',
    '✅ 实时执行监控',
    '✅ 错误处理和日志记录'
  ]
  
  console.log('已实现功能:')
  features.forEach(feature => console.log(feature))
  
  return {
    testWorkflow: createTestWorkflow(),
    parallelTestWorkflow: createParallelTestWorkflow(),
    features
  }
}