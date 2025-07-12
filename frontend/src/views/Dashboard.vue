<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2 class="page-title">政策分类总览</h2>
      </el-col>
    </el-row>
    
    <!-- 添加时间筛选组件 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <div class="filter-title">时间范围</div>
        <div class="filter-actions">
          <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
            <el-radio-button label="week">近一周</el-radio-button>
            <el-radio-button label="month">近一月</el-radio-button>
            <el-radio-button label="quarter">近三月</el-radio-button>
            <el-radio-button label="year">近一年</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      
      <div v-if="timeRange === 'custom'" class="custom-date-range">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="fetchData"
        />
      </div>
    </el-card>
    
    <el-row :gutter="20" v-loading="loading">
      <el-col
        v-for="cat in categories"
        :key="cat.name"
        :xs="24"
        :sm="12"
        :md="6"
        :lg="6"
        class="stat-card-col"
      >
        <el-card
          :body-style="{ padding: '20px' }"
          :class="{ 'has-update': cat.newCount > 0 }"
          class="stat-card"
        >
          <div class="stat-card-content">
            <div class="stat-card-icon">
              <el-icon :size="36" :color="getIconColor(cat.name)">
                <component :is="getCategoryIcon(cat.name)" />
              </el-icon>
            </div>
            <div class="stat-card-info">
              <div class="stat-card-title">{{ cat.name }}</div>
              <div class="stat-card-number">{{ cat.total }}</div>
              <div v-if="cat.newCount > 0" class="stat-card-update">
                今日新增 <span>+{{ cat.newCount }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" v-loading="loading">
          <div class="chart-title">政策分类分布</div>
          <v-chart :option="pieOption" autoresize class="chart" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" v-loading="trendLoading">
          <div class="chart-title">政策趋势</div>
          <v-chart :option="lineOption" autoresize class="chart" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from "echarts/core"
import VChart from "vue-echarts"
import { PieChart, LineChart } from "echarts/charts"
import { 
  TitleComponent, 
  TooltipComponent, 
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from "echarts/components"
import { CanvasRenderer } from "echarts/renderers"
import { categoryApi, policyApi } from '../api'
import { ElMessage } from 'element-plus'
import {
  Document,
  Money,
  User,
  Promotion,
  Connection,
  More
} from '@element-plus/icons-vue'

use([
  PieChart, 
  LineChart,
  TitleComponent, 
  TooltipComponent, 
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  CanvasRenderer
])

// 数据加载状态
const loading = ref(false)
const trendLoading = ref(false)

// 分类数据
const categories = ref([])

// 趋势数据
const trendData = ref({
  months: [],
  trends: []
})

// 时间范围筛选
const timeRange = ref('month') // 默认近一个月
const dateRange = ref([])

// 设置默认日期范围
const setDefaultDateRange = () => {
  const today = new Date()
  const end = new Date(today)
  let start = new Date(today)
  
  switch(timeRange.value) {
    case 'week':
      start.setDate(today.getDate() - 7)
      break
    case 'month':
      start.setMonth(today.getMonth() - 1)
      break
    case 'quarter':
      start.setMonth(today.getMonth() - 3)
      break
    case 'year':
      start.setFullYear(today.getFullYear() - 1)
      break
    default:
      start.setMonth(today.getMonth() - 1) // 默认一个月
  }
  
  // 格式化日期为YYYY-MM-DD
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  dateRange.value = [formatDate(start), formatDate(end)]
}

// 处理时间范围变化
const handleTimeRangeChange = () => {
  if (timeRange.value !== 'custom') {
    setDefaultDateRange()
    fetchData()
  }
}

// 获取所有数据
const fetchData = () => {
  fetchCategories()
  fetchTrends()
}

// 获取分类数据
const fetchCategories = async () => {
  loading.value = true
  try {
    // 构建查询参数，添加时间范围
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 这里假设后端API支持时间范围筛选
    categories.value = await categoryApi.getCategoryStats(params)
  } catch (error) {
    console.error('获取分类数据失败:', error)
    ElMessage.error('获取分类数据失败')
  } finally {
    loading.value = false
  }
}

// 获取趋势数据
const fetchTrends = async () => {
  trendLoading.value = true
  try {
    // 构建查询参数，添加时间范围
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 这里假设后端API支持时间范围筛选
    trendData.value = await policyApi.getPolicyTrends(params)
  } catch (error) {
    console.error('获取趋势数据失败:', error)
    ElMessage.error('获取趋势数据失败')
  } finally {
    trendLoading.value = false
  }
}

// 获取分类图标
const getCategoryIcon = (categoryName) => {
  const iconMap = {
    '增值税': Money,
    '企业所得税': Document,
    '个税': User,
    '出口退税': Promotion,
    '税收协定': Connection
  }
  return iconMap[categoryName] || More
}

// 获取图标颜色
const getIconColor = (categoryName) => {
  const colorMap = {
    '增值税': '#409EFF',
    '企业所得税': '#67C23A',
    '个税': '#E6A23C',
    '出口退税': '#F56C6C',
    '税收协定': '#909399'
  }
  return colorMap[categoryName] || '#909399'
}

// 饼图配置
const pieOption = computed(() => ({
  tooltip: { 
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: { 
    bottom: 10,
    left: 'center',
    itemWidth: 12,
    itemHeight: 12,
    textStyle: {
      fontSize: 12
    }
  },
  series: [
    {
      name: '政策数量',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: categories.value.map(cat => ({
        value: cat.total,
        name: cat.name
      }))
    }
  ]
}))

// 趋势图配置
const lineOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: trendData.value.trends?.map(item => item.name) || [],
    bottom: 10
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: trendData.value.months || []
  },
  yAxis: {
    type: 'value'
  },
  series: trendData.value.trends?.map(item => ({
    name: item.name,
    type: 'line',
    data: item.data,
    smooth: true,
    symbolSize: 6,
    lineStyle: {
      width: 3
    },
    areaStyle: {
      opacity: 0.1
    }
  })) || []
}))

// 页面加载时获取数据
onMounted(() => {
  setDefaultDateRange() // 设置默认日期范围
  fetchData()
})
</script>

<style scoped>
.dashboard-container {
  padding-bottom: 20px;
}

.page-title {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.custom-date-range {
  margin-top: 15px;
}

.stat-card-col {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.stat-card.has-update {
  border: 2px solid #f56c6c;
}

.stat-card-content {
  display: flex;
  align-items: center;
}

.stat-card-icon {
  margin-right: 16px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card-info {
  flex: 1;
}

.stat-card-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-card-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-card-update {
  margin-top: 10px;
  color: #f56c6c;
  font-size: 14px;
}

.stat-card-update span {
  font-size: 18px;
  font-weight: bold;
}

.chart-row {
  margin-top: 10px;
}

.chart-card {
  height: 100%;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.chart {
  height: 350px;
}

@media (max-width: 768px) {
  .chart {
    height: 250px;
  }
  
  .stat-card-number {
    font-size: 24px;
  }
  
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-actions {
    margin-top: 10px;
    width: 100%;
    overflow-x: auto;
  }
}
</style>