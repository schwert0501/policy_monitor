import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8090/api',
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证信息等
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 分类相关API
export const categoryApi = {
  // 获取所有分类
  getCategories() {
    return api.get('/categories').then(res => res.data.data);
  },
  
  // 获取单个分类
  getCategory(id) {
    return api.get(`/categories/${id}`).then(res => res.data.data);
  },
  
  // 获取分类统计数据
  getCategoryStats(params = {}) {
    return api.get('/categories/stats', { params }).then(res => {
      // 将后端返回的policy_count映射为前端需要的total和newCount字段
      return res.data.data.map(item => ({
        id: item.id,
        name: item.name,
        total: item.policy_count,
        newCount: 0 // 默认设置为0，因为后端暂时没有提供这个数据
      }));
    });
  }
};

// 政策相关API
export const policyApi = {
  // 获取所有政策
  getPolicies(params = {}) {
    return api.get('/policies', { params }).then(res => {
      if (res.data.success) {
        return {
          policies: res.data.data.policies || [],
          total: res.data.data.total || 0,
          pages: res.data.data.pages || 1,
          current_page: res.data.data.current_page || 1
        };
      }
      return { policies: [], total: 0, pages: 1, current_page: 1 };
    });
  },
  
  // 获取单个政策
  getPolicy(id) {
    return api.get(`/policies/${id}`).then(res => res.data.data);
  },
  
  // 获取政策趋势数据
  getPolicyTrends(params = {}) {
    return api.get('/policies/trends', { params }).then(res => {
      // 如果后端没有实现趋势API，返回模拟数据
      if (!res.data.success) {
        return {
          months: ['1月', '2月', '3月', '4月', '5月', '6月'],
          trends: [
            {
              name: '增值税',
              data: [10, 15, 20, 25, 22, 18]
            },
            {
              name: '企业所得税',
              data: [15, 12, 18, 22, 20, 16]
            },
            {
              name: '个税',
              data: [8, 10, 12, 15, 14, 10]
            }
          ]
        };
      }
      return res.data.data;
    });
  }
};

// 监测相关API
export const monitorApi = {
  // 运行监测任务
  runMonitor() {
    return api.post('/monitor/run').then(res => res.data);
  },
  
  // 获取监测统计数据
  getMonitorStats(days = 30) {
    return api.get(`/monitor/stats?days=${days}`).then(res => res.data.data);
  },
  
  // 获取监测到的政策列表
  getMonitoredPolicies(params = {}) {
    return api.get('/monitor/policies', { params }).then(res => res.data.data);
  },
  
  // 获取政策详情
  getPolicyDetail(id) {
    return api.get(`/monitor/policy/${id}`).then(res => res.data.data);
  }
};

export default api; 