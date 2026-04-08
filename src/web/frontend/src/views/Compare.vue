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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const compareList = ref([
  {
    id: 1,
    model: 'best_model.pth',
    segmented_image: '/api/placeholder/300/200',
    iou: 0.80,
    timestamp: '2026-04-07 16:30:00'
  },
  {
    id: 2,
    model: 'epoch_10.pth',
    segmented_image: '/api/placeholder/300/200',
    iou: 0.78,
    timestamp: '2026-04-07 16:31:00'
  }
])

const differenceTable = ref([
  { metric: 'IoU', model0: '80.00%', model1: '78.00%' },
  { metric: '准确率', model0: '92.00%', model1: '90.00%' },
  { metric: '处理时间', model0: '1.2s', model1: '1.3s' }
])

const removeFromCompare = (index) => {
  compareList.value.splice(index, 1)
  ElMessage.success('已移除')
}

const clearCompare = () => {
  compareList.value = []
  ElMessage.success('已清空对比列表')
}
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
