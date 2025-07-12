<template>
  <div class="monitor-page">
    <h1>政策监测</h1>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-title">监测时间范围</div>
        <div class="stat-value">{{ timeRange }}天</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">新增政策</div>
        <div class="stat-value">{{ stats.newPolicies }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">更新政策</div>
        <div class="stat-value">{{ stats.updatedPolicies }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">政策总数</div>
        <div class="stat-value">{{ stats.totalPolicies }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">上次监测时间</div>
        <div class="stat-value">{{ formatDateTime(stats.lastMonitorTime) }}</div>
      </div>
    </div>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="time-selector">
        <span>时间范围：</span>
        <select v-model="timeRange" @change="fetchData">
          <option :value="30">近30天</option>
          <option :value="90">近90天</option>
          <option :value="180">近180天</option>
          <option :value="365">近1年</option>
        </select>
      </div>
      <button class="run-monitor-btn" @click="runMonitor" :disabled="isMonitoring">
        {{ isMonitoring ? '监测中...' : '立即监测' }}
      </button>
    </div>
    
    <!-- 政策列表 -->
    <div class="policy-list">
      <table>
        <thead>
          <tr>
            <th>政策标题</th>
            <th>发布单位</th>
            <th>发布日期</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="policy in policies" :key="policy.id">
            <td>{{ policy.title }}</td>
            <td>{{ policy.org }}</td>
            <td>{{ formatDate(policy.pubDate) }}</td>
            <td>
              <span class="status-tag" :class="policy.status">
                {{ policy.status === 'new' ? '新增' : '更新' }}
              </span>
            </td>
            <td>
              <button class="view-btn" @click="viewPolicy(policy.id)">查看</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 0">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1"
        >上一页</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
        >下一页</button>
      </div>
      
      <div class="no-data" v-if="policies.length === 0">
        暂无政策数据
      </div>
    </div>
    
    <!-- 政策详情弹窗 -->
    <div class="policy-modal" v-if="showPolicyDetail">
      <div class="policy-modal-content">
        <div class="policy-modal-header">
          <h2>{{ currentPolicy.title }}</h2>
          <button class="close-btn" @click="closePolicyDetail">&times;</button>
        </div>
        <div class="policy-modal-body">
          <div class="policy-meta">
            <p><strong>发布单位：</strong>{{ currentPolicy.org }}</p>
            <p><strong>发布日期：</strong>{{ formatDate(currentPolicy.pubDate) }}</p>
            <p><strong>分类：</strong>{{ currentPolicy.category }}</p>
            <p v-if="currentPolicy.source_url">
              <strong>来源：</strong>
              <a :href="currentPolicy.source_url" target="_blank">{{ currentPolicy.source_url }}</a>
            </p>
          </div>
          <div class="policy-content">
            <pre>{{ currentPolicy.content }}</pre>
          </div>
        </div>
        <div class="policy-modal-footer">
          <button @click="closePolicyDetail">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { monitorApi } from '../api';

export default {
  name: 'MonitorView',
  data() {
    return {
      timeRange: 30,
      stats: {
        newPolicies: 0,
        updatedPolicies: 0,
        totalPolicies: 0,
        lastMonitorTime: null
      },
      policies: [],
      currentPage: 1,
      totalPages: 0,
      totalItems: 0,
      isMonitoring: false,
      showPolicyDetail: false,
      currentPolicy: {}
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        // 获取统计数据
        this.stats = await monitorApi.getMonitorStats(this.timeRange);
        
        // 获取政策列表
        await this.fetchPolicies();
      } catch (error) {
        console.error('获取监测数据失败', error);
        alert('获取监测数据失败');
      }
    },
    async fetchPolicies() {
      try {
        const params = {
          days: this.timeRange,
          page: this.currentPage,
          per_page: 10
        };
        const response = await monitorApi.getMonitoredPolicies(params);
        this.policies = response.policies;
        this.totalItems = response.total;
        this.totalPages = response.pages;
      } catch (error) {
        console.error('获取政策列表失败', error);
        alert('获取政策列表失败');
      }
    },
    async runMonitor() {
      if (this.isMonitoring) return;
      
      this.isMonitoring = true;
      try {
        const response = await monitorApi.runMonitor();
        if (response.success) {
          alert('监测任务已完成');
          // 刷新数据
          this.fetchData();
        } else {
          alert(`监测任务失败: ${response.message}`);
        }
      } catch (error) {
        console.error('运行监测任务失败', error);
        alert('运行监测任务失败');
      } finally {
        this.isMonitoring = false;
      }
    },
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchPolicies();
    },
    async viewPolicy(policyId) {
      try {
        this.currentPolicy = await monitorApi.getPolicyDetail(policyId);
        this.showPolicyDetail = true;
      } catch (error) {
        console.error('获取政策详情失败', error);
        alert('获取政策详情失败');
      }
    },
    closePolicyDetail() {
      this.showPolicyDetail = false;
      this.currentPolicy = {};
    },
    formatDate(dateStr) {
      if (!dateStr) return '未知';
      const date = new Date(dateStr);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '未知';
      const date = new Date(dateTimeStr);
      return `${this.formatDate(dateTimeStr)} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    }
  }
};
</script>

<style scoped>
.monitor-page {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

.stats-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  min-width: 180px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.time-selector select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-left: 10px;
}

.run-monitor-btn {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.run-monitor-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.policy-list {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

th {
  font-weight: 500;
  color: #606266;
  background-color: #f5f7fa;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.new {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-tag.updated {
  background-color: #ecf5ff;
  color: #409eff;
}

.view-btn {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.pagination button {
  padding: 5px 10px;
  border: 1px solid #dcdfe6;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.no-data {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

/* 政策详情弹窗 */
.policy-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.policy-modal-content {
  background-color: white;
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.policy-modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.policy-modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #909399;
}

.policy-modal-body {
  padding: 20px;
  overflow-y: auto;
  flex-grow: 1;
}

.policy-meta {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.policy-meta p {
  margin: 8px 0;
}

.policy-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.policy-modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #ebeef5;
  text-align: right;
}

.policy-modal-footer button {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}
</style> 