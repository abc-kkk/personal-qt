<template>
  <div class="app-container">
    <el-container>
      <el-aside width="200px" class="sidebar">
        <div class="logo-container">
          <h1 class="logo">量化交易</h1>
        </div>
        <el-menu
          :router="true"
          :default-active="activeMenu"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-sub-menu index="/investment">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>投资管理</span>
            </template>
            <el-menu-item index="/stock-trades">
              <el-icon><Histogram /></el-icon>
              <span>交易记录</span>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/categories">
            <el-icon><Files /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item index="/failure-cases">
            <el-icon><Warning /></el-icon>
            <span>失败案例</span>
          </el-menu-item>
          <el-menu-item index="/daily-reviews">
            <el-icon><Calendar /></el-icon>
            <span>每日复盘</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="app-header">
          <div class="header-left">
            <el-icon class="toggle-sidebar" @click="toggleSidebar"><Fold /></el-icon>
            <breadcrumb />
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-dropdown">
                <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></el-avatar>
                <span class="username">管理员</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人信息</el-dropdown-item>
                  <el-dropdown-item>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, TrendCharts, Histogram, Files, Warning, Calendar, Fold } from '@element-plus/icons-vue'
import Breadcrumb from '@/components/Breadcrumb.vue'

export default {
  name: 'App',
  components: {
    Breadcrumb,
    HomeFilled,
    TrendCharts,
    Histogram,
    Files,
    Warning,
    Calendar,
    Fold
  },
  setup() {
    const route = useRoute()
    const sidebarCollapsed = ref(false)
    
    const activeMenu = computed(() => {
      return route.path
    })
    
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
    
    return {
      activeMenu,
      sidebarCollapsed,
      toggleSidebar
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3649;
}

.logo {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.sidebar-menu {
  border-right: none;
  height: calc(100% - 60px);
}

.app-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  color: #606266;
}

.app-main {
  background-color: #f5f7fa;
  padding: 0;
  position: relative;
}

/* 覆盖 Element Plus 样式 */
.el-menu-item.is-active {
  background-color: #263445 !important;
}

.el-menu-item:hover, .el-sub-menu__title:hover {
  background-color: #263445 !important;
}
</style> 