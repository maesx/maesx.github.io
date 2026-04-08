<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="30"><PictureFilled /></el-icon>
        <span>图像分割平台</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/segment">
          <el-icon><Edit /></el-icon>
          <span>图像分割</span>
        </el-menu-item>
        
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
        
        <el-menu-item index="/compare">
          <el-icon><DataAnalysis /></el-icon>
          <span>结果对比</span>
        </el-menu-item>
        
        <el-menu-item index="/models">
          <el-icon><Folder /></el-icon>
          <span>模型管理</span>
        </el-menu-item>
        
        <el-menu-item index="/augmentation">
          <el-icon><MagicStick /></el-icon>
          <span>数据增强</span>
        </el-menu-item>
      </el-menu>
      
      <!-- GPU状态卡片 -->
      <div class="gpu-status" v-if="gpuInfo">
        <div class="gpu-header">
          <el-icon><Monitor /></el-icon>
          <span>GPU状态</span>
        </div>
        <div class="gpu-info">
          <p><strong>类型:</strong> {{ gpuInfo.type || 'CPU' }}</p>
          <p><strong>设备:</strong> {{ gpuInfo.device || 'CPU Only' }}</p>
          <p v-if="gpuInfo.memory">
            <strong>内存:</strong> 
            {{ gpuInfo.memory.used?.toFixed(1) || 0 }} / 
            {{ gpuInfo.memory.total?.toFixed(1) || gpuInfo.memory.recommended_max }} 
            {{ gpuInfo.type === 'MPS' ? 'MB' : 'GB' }}
          </p>
        </div>
      </div>
    </el-aside>
    
    <!-- 右侧主体 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="User" />
              <span class="username">{{ userInfo.name }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容区域 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { visualizationApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const gpuInfo = ref(null)
const userInfo = ref({
  name: 'Demo User',
  email: 'demo@example.com'
})

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => route.meta.title || '图像分割')

const fetchGPUStatus = async () => {
  try {
    const response = await visualizationApi.getGPUStatus()
    if (response.success) {
      gpuInfo.value = response.gpu
    }
  } catch (error) {
    console.error('获取GPU状态失败:', error)
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'logout':
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      ElMessage.success('已退出登录')
      break
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
  }
}

onMounted(() => {
  // 加载用户信息
  const user = localStorage.getItem('user')
  if (user) {
    userInfo.value = JSON.parse(user)
  }
  
  // 获取GPU状态
  fetchGPUStatus()
  setInterval(fetchGPUStatus, 5000) // 每5秒刷新一次
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.gpu-status {
  padding: 16px;
  margin: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  color: #fff;
}

.gpu-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: bold;
  color: #1890ff;
}

.gpu-info {
  font-size: 12px;
  line-height: 1.8;
}

.gpu-info p {
  margin: 0;
}

.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
}

.main {
  background: #f5f7fa;
  padding: 24px;
}
</style>
