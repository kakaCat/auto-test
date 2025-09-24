// 测试前端API调用的脚本
const axios = require('axios');

const BASE_URL = 'http://localhost:8001';

async function testAPIs() {
    console.log('开始测试前端API调用...\n');
    
    try {
        // 测试通用统计接口
        console.log('1. 测试通用统计接口...');
        const statsResponse = await axios.get(`${BASE_URL}/api/stats`);
        console.log('✅ 通用统计接口正常:', statsResponse.data.success);
        console.log('   - API数量:', statsResponse.data.data.api_stats.total_apis);
        console.log('   - 工作流数量:', statsResponse.data.data.workflow_stats.total_workflows);
        console.log('   - 场景数量:', statsResponse.data.data.scenario_stats.total_scenarios);
        
        // 测试API统计接口
        console.log('\n2. 测试API统计接口...');
        const apiStatsResponse = await axios.get(`${BASE_URL}/api/apis/stats`);
        console.log('✅ API统计接口正常:', apiStatsResponse.data.success);
        
        // 测试工作流统计接口
        console.log('\n3. 测试工作流统计接口...');
        const workflowStatsResponse = await axios.get(`${BASE_URL}/api/workflows/stats`);
        console.log('✅ 工作流统计接口正常:', workflowStatsResponse.data.success);
        
        // 测试场景统计接口
        console.log('\n4. 测试场景统计接口...');
        const scenarioStatsResponse = await axios.get(`${BASE_URL}/api/scenarios/stats`);
        console.log('✅ 场景统计接口正常:', scenarioStatsResponse.data.success);
        
        // 测试获取API列表
        console.log('\n5. 测试获取API列表...');
        const apisResponse = await axios.get(`${BASE_URL}/api/apis`);
        console.log('✅ API列表接口正常:', apisResponse.data.success);
        console.log('   - API列表长度:', apisResponse.data.data.length);
        
        // 测试获取工作流列表
        console.log('\n6. 测试获取工作流列表...');
        const workflowsResponse = await axios.get(`${BASE_URL}/api/workflows`);
        console.log('✅ 工作流列表接口正常:', workflowsResponse.data.success);
        console.log('   - 工作流列表长度:', workflowsResponse.data.data.length);
        
        // 测试获取场景列表
        console.log('\n7. 测试获取场景列表...');
        const scenariosResponse = await axios.get(`${BASE_URL}/api/scenarios`);
        console.log('✅ 场景列表接口正常:', scenariosResponse.data.success);
        console.log('   - 场景列表长度:', scenariosResponse.data.data.length);
        
        console.log('\n🎉 所有API测试通过！前端与后端集成正常。');
        
    } catch (error) {
        console.error('❌ API测试失败:', error.message);
        if (error.response) {
            console.error('   状态码:', error.response.status);
            console.error('   响应数据:', error.response.data);
        }
    }
}

testAPIs();