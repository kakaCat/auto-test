/**
 * 前端API调用测试脚本
 * 模拟用户在API管理页面的点击操作，检查是否存在API流程错误
 */

// Node.js环境兼容性处理
let fetch;
if (typeof window === 'undefined') {
    // Node.js环境
    try {
        fetch = require('node-fetch');
    } catch (e) {
        // 如果没有node-fetch，使用内置的http模块
        const https = require('https');
        const http = require('http');
        const { URL } = require('url');
        
        fetch = function(url, options = {}) {
            return new Promise((resolve, reject) => {
                const urlObj = new URL(url);
                const isHttps = urlObj.protocol === 'https:';
                const client = isHttps ? https : http;
                
                const requestOptions = {
                    hostname: urlObj.hostname,
                    port: urlObj.port || (isHttps ? 443 : 80),
                    path: urlObj.pathname + urlObj.search,
                    method: options.method || 'GET',
                    headers: options.headers || {}
                };
                
                const req = client.request(requestOptions, (res) => {
                    let data = '';
                    res.on('data', chunk => data += chunk);
                    res.on('end', () => {
                        const response = {
                            ok: res.statusCode >= 200 && res.statusCode < 300,
                            status: res.statusCode,
                            statusText: res.statusMessage,
                            json: () => Promise.resolve(JSON.parse(data)),
                            text: () => Promise.resolve(data)
                        };
                        resolve(response);
                    });
                });
                
                req.on('error', reject);
                
                if (options.body) {
                    req.write(options.body);
                }
                
                req.end();
            });
        };
    }
}

// 模拟前端环境
const API_BASE_URL = 'http://localhost:8000';

// 模拟axios请求
async function mockRequest(method, url, data = null, headers = {}) {
    const config = {
        method: method.toUpperCase(),
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    };

    if (data && (method.toUpperCase() === 'POST' || method.toUpperCase() === 'PUT' || method.toUpperCase() === 'PATCH')) {
        config.body = JSON.stringify(data);
    }

    try {
        console.log(`🔄 发送请求: ${method.toUpperCase()} ${url}`);
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        console.log(`✅ 请求成功: ${method.toUpperCase()} ${url}`, result);
        return result;
    } catch (error) {
        console.error(`❌ 请求失败: ${method.toUpperCase()} ${url}`, error.message);
        throw error;
    }
}

// 模拟API管理页面的操作流程
class ApiManagementTest {
    constructor() {
        this.selectedSystemId = null;
        this.selectedModuleId = null;
        this.apiList = [];
        this.systemList = [];
        this.moduleList = [];
        this.createdApiId = null;
    }

    // 1. 页面初始化 - 加载系统列表
    async initializePage() {
        console.log('\n🚀 开始页面初始化...');
        try {
            // 加载系统列表
            const systemResponse = await mockRequest('GET', `${API_BASE_URL}/api/systems/v1/`);
            this.systemList = systemResponse.data || [];
            console.log(`📋 系统列表加载成功，共 ${this.systemList.length} 个系统`);

            // 加载模块列表
            const moduleResponse = await mockRequest('GET', `${API_BASE_URL}/api/modules/v1/`);
            this.moduleList = moduleResponse.data || [];
            console.log(`📋 模块列表加载成功，共 ${this.moduleList.length} 个模块`);

            return true;
        } catch (error) {
            console.error('❌ 页面初始化失败:', error.message);
            return false;
        }
    }

    // 工具方法：根据系统ID选择一个匹配的模块ID
    findModuleForSystem(systemId) {
        if (!Array.isArray(this.moduleList)) return null;
        const mod = this.moduleList.find(m => (m.system_id ?? m.systemId) === systemId);
        return mod ? mod.id : null;
    }

    // 工具方法：找到至少包含一个模块的系统ID
    findSystemWithModules() {
        if (!Array.isArray(this.systemList) || !Array.isArray(this.moduleList)) return null;
        for (const sys of this.systemList) {
            const mod = this.moduleList.find(m => (m.system_id ?? m.systemId) === sys.id);
            if (mod) return sys.id;
        }
        return null;
    }

    // 2. 选择系统 - 模拟用户点击系统节点
    async selectSystem(systemId) {
        console.log(`\n🎯 选择系统: ${systemId}`);
        try {
            this.selectedSystemId = systemId;
            this.selectedModuleId = null;

            // 加载该系统的API列表
            const apiResponse = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/`, null, {
                'X-System-ID': systemId
            });
            const data = apiResponse.data || {};
            this.apiList = data.apis || data.list || (Array.isArray(data) ? data : []);
            const count = Array.isArray(this.apiList) ? this.apiList.length : 0;
            console.log(`📋 系统 ${systemId} 的API列表加载成功，共 ${count} 个API`);
            return true;
        } catch (error) {
            console.error(`❌ 选择系统失败: ${error.message}`);
            return false;
        }
    }

    // 3. 选择模块 - 模拟用户点击模块节点
    async selectModule(moduleId) {
        console.log(`\n🎯 选择模块: ${moduleId}`);
        try {
            this.selectedModuleId = moduleId;

            // 加载该模块的API列表
            const params = new URLSearchParams({
                module_id: moduleId
            });
            
            const apiResponse = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/?${params}`);
            const data = apiResponse.data || {};
            this.apiList = data.apis || data.list || (Array.isArray(data) ? data : []);
            const count = Array.isArray(this.apiList) ? this.apiList.length : 0;
            console.log(`📋 模块 ${moduleId} 的API列表加载成功，共 ${count} 个API`);
            return true;
        } catch (error) {
            console.error(`❌ 选择模块失败: ${error.message}`);
            return false;
        }
    }

    // 4. 新增API - 模拟用户点击新增按钮
    async createApi() {
        console.log('\n➕ 创建新API...');
        try {
            const moduleId = this.selectedModuleId || this.findModuleForSystem(this.selectedSystemId || 1) || 1;
            const newApiData = {
                system_id: this.selectedSystemId || 1,
                module_id: moduleId,
                name: '测试API',
                description: '这是一个测试API',
                method: 'GET',
                path: '/api/test',
                version: '1.0.0',
                status: 'active',
                auth_required: 1,
                rate_limit: 1000,
                timeout: 30
            };

            const response = await mockRequest('POST', `${API_BASE_URL}/api/api-interfaces/v1/`, newApiData);
            if (response && response.success === false) {
                console.error('❌ API创建返回失败:', response.message);
                return null;
            }
            const createdId = response?.data?.id ?? response?.id ?? null;
            if (createdId) {
                this.createdApiId = createdId;
                if (!Array.isArray(this.apiList)) this.apiList = [];
                this.apiList.unshift({ id: createdId, name: newApiData.name });
            }
            console.log('✅ API创建成功:', response);
            return response;
        } catch (error) {
            console.error(`❌ API创建失败: ${error.message}`);
            return null;
        }
    }

    // 5. 编辑API - 模拟用户点击编辑按钮
    async editApi(apiId) {
        console.log(`\n✏️ 编辑API: ${apiId}`);
        try {
            // 先获取API详情
            const detailResponse = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`);
            console.log('📄 API详情获取成功:', detailResponse);

            // 更新API
            const updateData = {
                description: '更新后的API描述',
                timeout: 60
            };

            const updateResponse = await mockRequest('PUT', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`, updateData);
            console.log('✅ API更新成功:', updateResponse);
            return updateResponse;
        } catch (error) {
            console.error(`❌ API编辑失败: ${error.message}`);
            return null;
        }
    }

    // 6. 测试API - 模拟用户点击测试按钮
    async testApi(apiId) {
        console.log(`\n🧪 测试API: ${apiId}`);
        try {
            const testData = {
                headers: {},
                params: {},
                body: {}
            };

            const response = await mockRequest('POST', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}/test`, testData);
            console.log('✅ API测试成功:', response);
            return response;
        } catch (error) {
            console.error(`❌ API测试失败: ${error.message}`);
            return null;
        }
    }

    // 分段保存：仅更新 request_schema
    async segmentedSaveRequestSchema(apiId) {
        console.log(`\n🧩 分段保存 request_schema: ${apiId}`);
        try {
            const reqSchemaStr = JSON.stringify({
                user_id: { type: 'number', required: true },
                q: { type: 'string' }
            });
            const updateResponse = await mockRequest('PUT', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`, { request_schema: reqSchemaStr });
            const detailResponse = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`);
            const data = detailResponse.data || detailResponse;
            const schema = data.request_schema || (data.data ? data.data.request_schema : undefined);
            const parsed = typeof schema === 'string' ? JSON.parse(schema) : schema;
            const ok = parsed && typeof parsed === 'object' && parsed.user_id && parsed.q;
            console.log(`✅ 分段保存 request_schema 校验: ${ok ? '通过' : '失败'}`);
            return ok;
        } catch (error) {
            console.error(`❌ 分段保存 request_schema 失败: ${error.message}`);
            return false;
        }
    }

    // 分段保存：仅更新 response_schema
    async segmentedSaveResponseSchema(apiId) {
        console.log(`\n🧩 分段保存 response_schema: ${apiId}`);
        try {
            const respSchemaStr = JSON.stringify({
                code: { type: 'number' },
                data: { type: 'object' }
            });
            const updateResponse = await mockRequest('PUT', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`, { response_schema: respSchemaStr });
            const detailResponse = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`);
            const data = detailResponse.data || detailResponse;
            const schema = data.response_schema || (data.data ? data.data.response_schema : undefined);
            const parsed = typeof schema === 'string' ? JSON.parse(schema) : schema;
            const ok = parsed && typeof parsed === 'object' && parsed.code && parsed.data;
            console.log(`✅ 分段保存 response_schema 校验: ${ok ? '通过' : '失败'}`);
            return ok;
        } catch (error) {
            console.error(`❌ 分段保存 response_schema 失败: ${error.message}`);
            return false;
        }
    }

    // 分段保存：仅更新 tags 与 auth_required
    async segmentedSaveTagsAndAuth(apiId) {
        console.log(`\n🧩 分段保存 tags/auth: ${apiId}`);
        try {
            const updateResponse = await mockRequest('PUT', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`, { tags: 'fast,internal', auth_required: 0 });
            const detailResponse = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`);
            const raw = detailResponse.data || detailResponse;
            const entity = raw.data ? raw.data : raw;
            // 后端响应模型不包含 tags_list（Service层会生成，但模型过滤），因此在缺失时从 tags 字符串回退解析
            let tagsList = entity.tags_list;
            if (!Array.isArray(tagsList) || tagsList.length === 0) {
                const tagsStr = entity.tags;
                if (typeof tagsStr === 'string') {
                    tagsList = tagsStr.split(',').map(s => s.trim()).filter(Boolean);
                } else {
                    tagsList = [];
                }
            }
            const auth = entity.auth_required;
            const ok = Array.isArray(tagsList) && tagsList.includes('fast') && tagsList.includes('internal') && Number(auth) === 0;
            console.log(`✅ 分段保存 tags/auth 校验: ${ok ? '通过' : '失败'}`);
            return ok;
        } catch (error) {
            console.error(`❌ 分段保存 tags/auth 失败: ${error.message}`);
            return false;
        }
    }

    // 7. 删除API - 模拟用户点击删除按钮
    async deleteApi(apiId) {
        console.log(`\n🗑️ 删除API: ${apiId}`);
        try {
            const response = await mockRequest('DELETE', `${API_BASE_URL}/api/api-interfaces/v1/${apiId}`);
            console.log('✅ API删除成功:', response);
            return response;
        } catch (error) {
            console.error(`❌ API删除失败: ${error.message}`);
            return null;
        }
    }

    // 8. 批量操作 - 模拟用户批量选择和操作
    async batchOperations() {
        console.log('\n📦 批量操作测试...');
        try {
            if (!Array.isArray(this.apiList) || this.apiList.length === 0) {
                console.log('⚠️ 没有可用的API进行批量操作，尝试重新加载列表');
                if (this.selectedModuleId) {
                    await this.selectModule(this.selectedModuleId);
                } else if (this.selectedSystemId) {
                    await this.selectSystem(this.selectedSystemId);
                }
            }
            if (!Array.isArray(this.apiList) || this.apiList.length === 0) {
                console.log('⚠️ 仍然没有可用的API进行批量操作');
                return false;
            }

            const apiIds = this.apiList.slice(0, 2).map(api => api.id); // 选择前两个API
            console.log(`📋 选择的API IDs: ${apiIds.join(', ')}`);

            // 批量测试
            const batchTestData = {
                api_ids: apiIds,
                headers: {},
                timeout: 30
            };

            const batchTestResponse = await mockRequest('POST', `${API_BASE_URL}/api/api-interfaces/v1/batch/test`, batchTestData);
            console.log('✅ 批量测试成功:', batchTestResponse);

            return true;
        } catch (error) {
            console.error(`❌ 批量操作失败: ${error.message}`);
            return false;
        }
    }

    // 9. 搜索功能 - 模拟用户搜索API
    async searchApis(keyword) {
        console.log(`\n🔍 搜索API: "${keyword}"`);
        try {
            const params = new URLSearchParams({
                keyword: keyword,
                system_id: this.selectedSystemId || '',
                module_id: this.selectedModuleId || ''
            });

            const response = await mockRequest('GET', `${API_BASE_URL}/api/api-interfaces/v1/?${params}`);
            console.log(`✅ 搜索成功，找到 ${response.data?.length || 0} 个API`);
            return response;
        } catch (error) {
            console.error(`❌ 搜索失败: ${error.message}`);
            return null;
        }
    }

    // 完整的用户操作流程测试
    async runCompleteTest() {
        console.log('🎬 开始完整的API管理流程测试...\n');
        
        const results = {
            initialization: false,
            systemSelection: false,
            moduleSelection: false,
            apiCreation: false,
            segmentedRequestSchema: false,
            segmentedResponseSchema: false,
            segmentedTagsAuth: false,
            apiEditing: false,
            apiTesting: false,
            apiDeletion: false,
            batchOperations: false,
            searching: false
        };

        try {
            // 1. 页面初始化
            results.initialization = await this.initializePage();
            if (!results.initialization) {
                throw new Error('页面初始化失败');
            }

            // 2. 选择系统（选择一个至少包含一个模块的系统）
            let targetSystemId = null;
            if (this.systemList.length > 0) {
                targetSystemId = this.findSystemWithModules() || this.systemList[0].id;
                results.systemSelection = await this.selectSystem(targetSystemId);
            }

            // 3. 选择模块（选择该系统对应的模块）
            let targetModuleId = null;
            if (this.moduleList.length > 0) {
                targetModuleId = this.findModuleForSystem(targetSystemId) || this.moduleList[0].id;
                results.moduleSelection = await this.selectModule(targetModuleId);
            }

            // 4. 创建API
            const newApi = await this.createApi();
            results.apiCreation = newApi !== null;
            const apiId = (newApi && newApi.data && newApi.data.id) ? newApi.data.id : this.createdApiId;

            // 4.1 分段保存：request_schema
            if (apiId) {
                results.segmentedRequestSchema = await this.segmentedSaveRequestSchema(apiId);
            }
            // 4.2 分段保存：response_schema
            if (apiId) {
                results.segmentedResponseSchema = await this.segmentedSaveResponseSchema(apiId);
            }
            // 4.3 分段保存：tags/auth
            if (apiId) {
                results.segmentedTagsAuth = await this.segmentedSaveTagsAndAuth(apiId);
            }

            // 5. 编辑API
            if (apiId) {
                results.apiEditing = await this.editApi(apiId) !== null;
            }

            // 6. 测试API
            if (apiId) {
                results.apiTesting = await this.testApi(apiId) !== null;
            }

            // 7. 批量操作
            results.batchOperations = await this.batchOperations();

            // 8. 搜索功能
            results.searching = await this.searchApis('用户') !== null;

            // 9. 删除API (如果创建了新的API)
            if (apiId) {
                results.apiDeletion = await this.deleteApi(apiId) !== null;
            }

        } catch (error) {
            console.error('🚨 测试过程中发生错误:', error.message);
        }

        // 输出测试结果
        console.log('\n📊 测试结果汇总:');
        console.log('==================');
        Object.entries(results).forEach(([test, passed]) => {
            const status = passed ? '✅ 通过' : '❌ 失败';
            console.log(`${test.padEnd(20)}: ${status}`);
        });

        const passedCount = Object.values(results).filter(Boolean).length;
        const totalCount = Object.keys(results).length;
        console.log(`\n总体结果: ${passedCount}/${totalCount} 项测试通过`);

        return results;
    }
}

// 运行测试
async function runTest() {
    const tester = new ApiManagementTest();
    await tester.runCompleteTest();
}

// 如果在Node.js环境中运行
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiManagementTest, runTest };
}

// 如果在浏览器环境中运行
if (typeof window !== 'undefined') {
    window.ApiManagementTest = ApiManagementTest;
    window.runApiTest = runTest;
}

// 自动运行测试
runTest().catch(console.error);