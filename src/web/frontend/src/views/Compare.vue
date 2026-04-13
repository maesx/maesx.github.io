<template>
  <div class="compare-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>结果对比</span>
          <el-button type="primary" size="small" @click="clearCompare">
            清空列表
          </el-button>
        </div>
      </template>
      
      <div v-if="compareList.length === 0" class="empty-state">
        <el-empty description="请从历史记录中选择需要对比的结果" />
      </div>
      
      <div v-else class="compare-content">
        <div class="compare-grid">
          <div v-for="(item, index) in compareList" :key="item.id" class="compare-item">
            <div class="item-header">
              <h3>{{ item.model }}</h3>
              <el-button 
                text 
                type="danger" 
                @click="removeFromCompare(index)"
              >
                移除
              </el-button>
            </div>
            
            <div class="item-image">
              <img :src="item.segmented_image" alt="分割结果" />
            </div>
            
            <div class="item-metrics">
              <p><strong>IoU:</strong> {{ (item.iou * 100).toFixed(2) }}%</p>
              <p><strong>时间:</strong> {{ item.timestamp }}</p>
            </div>
          </div>
        </div>
        
        <!-- 差异对比 -->
        <div class="difference-analysis">
          <h3>差异分析</h3>
          <el-table :data="differenceTable" stripe>
            <el-table-column prop="metric" label="指标" width="200" />
            <el-table-column v-for="(item, index) in compareList" :key="index" :label="item.model">
              <template #default="scope">
                {{ scope.row[`model${index}`] }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { segmentApi } from '@/api/modules'

const compareList = ref([])
const loading = ref(false)

// 计算差异对比表格数据
const differenceTable = computed(() => {
  if (compareList.value.length === 0) return []
  
  const metrics = ['IoU', '准确率', '处理时间']
  return metrics.map(metric => {
    const row = { metric }
    compareList.value.forEach((item, index) => {
      if (metric === 'IoU') {
        row[`model${index}`] = `${(item.iou * 100).toFixed(2)}%`
      } else if (metric === '准确率') {
        row[`model${index}`] = item.accuracy ? `${(item.accuracy * 100).toFixed(2)}%` : 'N/A'
      } else if (metric === '处理时间') {
        row[`model${index}`] = item.process_time ? `${item.process_time.toFixed(2)}s` : 'N/A'
      }
    })
    return row
  })
})

// 从历史记录获取对比列表
const fetchCompareList = async () => {
  loading.value = true
  try {
    const response = await segmentApi.getCompareList()
    if (response.success) {
      compareList.value = response.compare_list || []
    }
  } catch (error) {
    console.error('获取对比列表失败:', error)
    // 如果API不存在，初始为空列表
    compareList.value = []
  } finally {
    loading.value = false
  }
}

const removeFromCompare = async (index) => {
  const item = compareList.value[index]
  try {
    // 调用后端API移除
    await segmentApi.removeFromCompare(item.id)
    compareList.value.splice(index, 1)
    ElMessage.success('已移除')
  } catch (error) {
    console.error('移除失败:', error)
    // 即使API失败，也从本地移除
    compareList.value.splice(index, 1)
    ElMessage.success('已移除')
  }
}

const clearCompare = async () => {
  try {
    // 调用后端API清空
    await segmentApi.clearCompare()
    compareList.value = []
    ElMessage.success('已清空对比列表')
  } catch (error) {
    console.error('清空失败:', error)
    // 即使API失败，也清空本地列表
    compareList.value = []
    ElMessage.success('已清空对比列表')
  }
}

onMounted(() => {
  fetchCompareList()
})
</script>

<style scoped>
.compare-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.compare-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-header h3 {
  margin: 0;
  font-size: 16px;
}

.item-image {
  margin-bottom: 12px;
}

.item-image img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.item-metrics {
  font-size: 14px;
  line-height: 1.8;
}

.difference-analysis {
  margin-top: 30px;
}

.difference-analysis h3 {
  margin-bottom: 16px;
  color: #606266;
}
</style>
