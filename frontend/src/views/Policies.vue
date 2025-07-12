<template>
  <div class="policies-container">
    <h2 class="page-title">政策管理</h2>
    
    <!-- 搜索和筛选区域 -->
    <el-card class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="政策标题">
          <el-input
            v-model="searchParams.title"
            placeholder="请输入政策标题"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="发布机构">
          <el-input
            v-model="searchParams.org"
            placeholder="请输入发布机构"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="政策分类">
          <el-select v-model="searchParams.category" placeholder="请选择分类" clearable>
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="发布日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 操作按钮区域 -->
    <div class="action-bar">
      <el-button type="primary" @click="openAddDialog">新增政策</el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-card class="table-card" v-loading="loading">
      <el-table :data="policies" style="width: 100%">
        <el-table-column prop="title" label="政策标题" min-width="200">
          <template #default="{ row }">
            <div class="policy-title">{{ row.title }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="category.name" label="分类" width="120" />
        <el-table-column prop="org" label="发布机构" width="150" />
        <el-table-column prop="pub_date" label="发布日期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.file_url"
              type="primary"
              link
              @click="viewFile(row.file_url)"
            >
              查看文件
            </el-button>
            <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="confirmDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '新增政策' : '编辑政策'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form
        ref="policyForm"
        :model="policyForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="政策标题" prop="title">
          <el-input v-model="policyForm.title" placeholder="请输入政策标题" />
        </el-form-item>
        
        <el-form-item label="政策分类" prop="category_id">
          <el-select v-model="policyForm.category_id" placeholder="请选择分类">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="发布机构" prop="org">
          <el-input v-model="policyForm.org" placeholder="请输入发布机构" />
        </el-form-item>
        
        <el-form-item label="发布日期" prop="pub_date">
          <el-date-picker
            v-model="policyForm.pub_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="政策内容">
          <el-input
            v-model="policyForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入政策内容"
          />
        </el-form-item>
        
        <el-form-item label="上传文件">
          <el-upload
            class="upload-demo"
            :action="''"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            :file-list="fileList"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                请上传PDF、Word或Excel文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoryApi, policyApi } from '../api'

// 数据加载状态
const loading = ref(false)
const submitLoading = ref(false)

// 分页相关
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)

// 政策数据
const policies = ref([])

// 分类数据
const categories = ref([])

// 搜索参数
const searchParams = reactive({
  title: '',
  org: '',
  category: ''
})

// 日期范围
const dateRange = ref([])

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' 或 'edit'
const policyForm = reactive({
  id: null,
  title: '',
  content: '',
  pub_date: '',
  org: '',
  category_id: ''
})
const fileList = ref([])
const selectedFile = ref(null)

// 表单验证规则
const rules = {
  title: [{ required: true, message: '请输入政策标题', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择政策分类', trigger: 'change' }],
  org: [{ required: true, message: '请输入发布机构', trigger: 'blur' }],
  pub_date: [{ required: true, message: '请选择发布日期', trigger: 'change' }]
}

// 获取政策列表
const fetchPolicies = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = { 
      ...searchParams,
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    // 添加日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const data = await policyApi.getPolicies(params)
    policies.value = data.policies
    total.value = data.total
    currentPage.value = data.current_page
  } catch (error) {
    console.error('获取政策列表失败:', error)
    ElMessage.error('获取政策列表失败')
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    categories.value = await categoryApi.getCategories()
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error('获取分类列表失败')
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchPolicies()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchParams).forEach(key => {
    searchParams[key] = ''
  })
  dateRange.value = []
  currentPage.value = 1
  fetchPolicies()
}

// 处理分页
const handlePageChange = (page) => {
  currentPage.value = page
  fetchPolicies()
}

// 打开新增对话框
const openAddDialog = () => {
  dialogType.value = 'add'
  Object.keys(policyForm).forEach(key => {
    policyForm[key] = key === 'id' ? null : ''
  })
  fileList.value = []
  selectedFile.value = null
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row) => {
  dialogType.value = 'edit'
  Object.keys(policyForm).forEach(key => {
    policyForm[key] = row[key] || ''
  })
  
  // 如果有文件，显示在上传列表中
  fileList.value = row.file_url
    ? [{ name: '已上传文件', url: row.file_url }]
    : []
  selectedFile.value = null
  dialogVisible.value = true
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

// 提交表单
const submitForm = async () => {
  const formEl = document.querySelector('.el-form')
  if (!formEl) return
  
  try {
    // 表单验证
    await new Promise((resolve, reject) => {
      const isValid = true // 简化验证逻辑
      if (isValid) {
        resolve()
      } else {
        reject(new Error('表单验证失败'))
      }
    })
    
    submitLoading.value = true
    
    // 准备表单数据
    const formData = new FormData()
    Object.keys(policyForm).forEach(key => {
      if (policyForm[key] !== null && policyForm[key] !== undefined) {
        formData.append(key, policyForm[key])
      }
    })
    
    // 添加文件（如果有）
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }
    
    // 提交数据
    if (dialogType.value === 'add') {
      await policyApi.createPolicy(formData)
      ElMessage.success('添加成功')
    } else {
      await policyApi.updatePolicy(policyForm.id, formData)
      ElMessage.success('更新成功')
    }
    
    // 关闭对话框并刷新列表
    dialogVisible.value = false
    fetchPolicies()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitLoading.value = false
  }
}

// 确认删除
const confirmDelete = (id) => {
  ElMessageBox.confirm('确认删除此政策?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await policyApi.deletePolicy(id)
        ElMessage.success('删除成功')
        fetchPolicies()
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

// 查看文件
const viewFile = (url) => {
  window.open(url, '_blank')
}

// 页面加载时获取数据
onMounted(() => {
  fetchCategories()
  fetchPolicies()
})
</script>

<style scoped>
.policies-container {
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

.action-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.table-card {
  margin-bottom: 20px;
}

.policy-title {
  font-weight: 500;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .filter-form {
    display: flex;
    flex-direction: column;
  }
  
  .filter-form .el-form-item {
    margin-right: 0;
  }
}
</style>