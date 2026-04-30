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
        <el-table-column prop="display_id" label="ID" width="120" />
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
    
    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="分割详情"
      width="90%"
      :close-on-click-modal="false"
    >
      <div v-if="currentDetail" class="detail-content">
        <!-- 基本信息 -->
        <el-descriptions :column="3" border class="detail-info">
          <el-descriptions-item label="记录ID">{{ currentDetail.display_id }}</el-descriptions-item>
          <el-descriptions-item label="使用模型">{{ currentDetail.model }}</el-descriptions-item>
          <el-descriptions-item label="分割类型">
            <el-tag>{{ currentDetail.segment_type === 'semantic' ? '语义分割' : '实例分割' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IoU得分">
            <el-tag :type="getIOUTagType(currentDetail.iou)">
              {{ (currentDetail.iou * 100).toFixed(2) }}%
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="准确率">{{ (currentDetail.accuracy * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="处理耗时">{{ currentDetail.process_time.toFixed(2) }}s</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="3">{{ currentDetail.timestamp }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 图像展示 -->
        <div class="image-grid">
          <div class="image-item">
            <h4>原图</h4>
            <img :src="currentDetail.thumbnail" alt="原图" class="detail-image" />
          </div>
          <div class="image-item">
            <h4>分割结果</h4>
            <img :src="currentDetail.segmented_image" alt="分割结果" class="detail-image" />
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="detail-actions">
          <el-button type="primary" @click="downloadImage(currentDetail.segmented_image, 'segmented.png')">
            <el-icon><Download /></el-icon>
            下载分割结果
          </el-button>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { segmentApi } from '@/api/modules'

const historyList = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const currentDetail = ref(null)

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
  currentDetail.value = row
  detailDialogVisible.value = true
}

const addToCompare = async (row) => {
  try {
    // 使用原始ID进行对比列表关联
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
    
    // 调用后端API删除
    const response = await segmentApi.deleteHistory(row.id)
    
    if (response.success) {
      // 从本地列表中移除
      const index = historyList.value.findIndex(item => item.id === row.id)
      if (index > -1) {
        historyList.value.splice(index, 1)
      }
      ElMessage.success(response.message || '删除成功')
    } else {
      ElMessage.error(response.error || '删除失败')
    }
  } catch (error) {
    // 用户取消删除
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const downloadImage = (base64Data, filename) => {
  try {
    // 创建下载链接
    const link = document.createElement('a')
    link.href = base64Data
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
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

.detail-content {
  padding: 20px;
}

.detail-info {
  margin-bottom: 24px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.image-item {
  text-align: center;
}

.image-item h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 14px;
}

.detail-image {
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
