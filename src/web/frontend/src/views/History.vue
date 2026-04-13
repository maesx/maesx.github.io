<template>
  <div class="history-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史记录</span>
          <el-button type="primary" size="small" @click="refreshHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
      
      <!-- 空状态 -->
      <el-empty v-else-if="historyList.length === 0" description="暂无历史记录" />
      
      <!-- 历史记录表格 -->
      <el-table v-else :data="historyList" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model" label="模型" width="180" />
        <el-table-column label="原图" width="120">
          <template #default="scope">
            <img :src="scope.row.thumbnail" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;" />
          </template>
        </el-table-column>
        <el-table-column prop="iou" label="IoU" width="100">
          <template #default="scope">
            <el-tag :type="getIOUTagType(scope.row.iou)">
              {{ (scope.row.iou * 100).toFixed(2) }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="addToCompare(scope.row)">对比</el-button>
            <el-button size="small" type="danger" @click="deleteRecord(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { segmentApi } from '@/api/modules'

const historyList = ref([])
const loading = ref(false)

const getIOUTagType = (iou) => {
  if (iou >= 0.8) return 'success'
  if (iou >= 0.6) return 'warning'
  return 'info'
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await segmentApi.getHistory()
    if (response.success) {
      historyList.value = response.history || []
      if (historyList.value.length === 0) {
        ElMessage.info('暂无历史记录')
      }
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const refreshHistory = () => {
  fetchHistory()
  ElMessage.success('刷新历史记录')
}

const viewDetail = (row) => {
  // TODO: 实现查看详情弹窗
  ElMessage.info(`查看详情: ${row.id}`)
}

const addToCompare = async (row) => {
  try {
    const response = await segmentApi.addToCompare(row.id)
    if (response.success) {
      ElMessage.success('已添加到对比列表')
    }
  } catch (error) {
    console.error('添加对比失败:', error)
    ElMessage.error('添加对比失败')
  }
}

const deleteRecord = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条历史记录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 从本地列表中移除
    const index = historyList.value.findIndex(item => item.id === row.id)
    if (index > -1) {
      historyList.value.splice(index, 1)
      ElMessage.success('已删除')
    }
  } catch (error) {
    // 用户取消删除
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.history-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-container p {
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}
</style>
