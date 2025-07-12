<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 当前激活的菜单项
const activeIndex = computed(() => route.path)
</script>

<template>
  <div class="app-container">
    <el-container>
      <el-header class="app-header">
        <div class="logo">财税政策管理系统</div>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="activeIndex"
          class="nav-menu"
        >
          <el-menu-item index="/">仪表盘</el-menu-item>
          <el-menu-item index="/policies">政策管理</el-menu-item>
          <el-menu-item index="/monitor">政策监测</el-menu-item>
        </el-menu>
      </el-header>
      
      <el-main class="app-main">
        <router-view />
      </el-main>
      
      <el-footer class="app-footer">
        &copy; 2025 财税政策管理系统
      </el-footer>
    </el-container>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-right: 40px;
}

.nav-menu {
  border-bottom: none;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 15px 0;
  background-color: #fff;
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    padding: 10px;
    height: auto !important;
  }
  
  .logo {
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  .app-main {
    padding: 10px;
  }
}
</style>