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
      
      <el-table :data="historyList" stripe style="width: 100%">
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
import { ElMessage } from 'element-plus'

const historyList = ref([
  {
    id: 1,
    model: 'best_model.pth',
    thumbnail: '/api/placeholder/80/60',
    iou: 0.80,
    timestamp: '2026-04-07 16:30:00'
  },
  {
    id: 2,
    model: 'epoch_10.pth',
    thumbnail: '/api/placeholder/80/60',
    iou: 0.78,
    timestamp: '2026-04-07 16:31:00'
  }
])

const getIOUTagType = (iou) => {
  if (iou >= 0.8) return 'success'
  if (iou >= 0.6) return 'warning'
  return 'info'
}

const refreshHistory = () => {
  ElMessage.success('刷新历史记录')
}

const viewDetail = (row) => {
  ElMessage.info(`查看详情: ${row.id}`)
}

const addToCompare = (row) => {
  ElMessage.success(`已添加到对比列表`)
}

const deleteRecord = (row) => {
  ElMessage.warning(`删除记录: ${row.id}`)
}

onMounted(() => {
  // TODO: 从API加载历史记录
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
</style>
