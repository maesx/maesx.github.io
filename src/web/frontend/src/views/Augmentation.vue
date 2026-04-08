<template>
  <div class="augmentation-container">
    <el-card>
      <template #header>
        <span>数据增强说明</span>
      </template>
      
      <div class="intro-section">
        <el-alert
          title="什么是数据增强？"
          type="info"
          :closable="false"
          show-icon
        >
          <p>
            数据增强是对训练图片进行各种变换，生成更多样化的训练样本，帮助模型学习更鲁棒的特征，提高泛化能力。
            注意：此处仅展示增强效果，模型训练时已自动应用。
          </p>
        </el-alert>
      </div>
      
      <div class="augmentation-grid">
        <div v-for="aug in augmentations" :key="aug.name" class="augmentation-card">
          <div class="aug-header">
            <h3>{{ aug.name }}</h3>
            <el-tag :type="getComplexityType(aug.complexity)" size="small">
              {{ aug.complexity }}
            </el-tag>
          </div>
          
          <div class="aug-content">
            <p class="description">{{ aug.description }}</p>
            
            <div class="params">
              <h4>参数设置:</h4>
              <ul>
                <li v-for="(value, key) in aug.params" :key="key">
                  <strong>{{ key }}:</strong> {{ value }}
                </li>
              </ul>
            </div>
            
            <div class="use-case">
              <h4>应用场景:</h4>
              <p>{{ aug.use_case }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="summary-section">
        <h3>增强效果总结</h3>
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="summary-card">
              <el-statistic title="增强方法总数" :value="summary.total_count" />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <h4>增强分类</h4>
              <el-tag v-for="(items, category) in summary.categories" :key="category" style="margin: 4px">
                {{ category }}: {{ items.length }}种
              </el-tag>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <h4>核心优势</h4>
              <ul>
                <li v-for="benefit in summary.benefits" :key="benefit">
                  {{ benefit }}
                </li>
              </ul>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { augmentationApi } from '@/api/modules'

const augmentations = ref([])
const summary = ref({
  total_count: 0,
  categories: {},
  benefits: []
})

const fetchAugmentations = async () => {
  try {
    const response = await augmentationApi.getAugmentations()
    if (response.success) {
      augmentations.value = response.augmentations
      summary.value = response.summary
    }
  } catch (error) {
    console.error('获取数据增强信息失败:', error)
  }
}

const getComplexityType = (complexity) => {
  const types = {
    '低': 'success',
    '中': 'warning',
    '高': 'danger'
  }
  return types[complexity] || 'info'
}

onMounted(() => {
  fetchAugmentations()
})
</script>

<style scoped>
.augmentation-container {
  padding: 20px;
}

.intro-section {
  margin-bottom: 24px;
}

.intro-section p {
  margin: 0;
  font-size: 14px;
}

.augmentation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.augmentation-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  transition: box-shadow 0.3s;
}

.augmentation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.aug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.aug-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.aug-content {
  font-size: 14px;
}

.description {
  color: #606266;
  margin-bottom: 12px;
}

.params, .use-case {
  margin-top: 12px;
}

.params h4, .use-case h4 {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.params ul {
  padding-left: 20px;
  margin: 0;
  line-height: 1.6;
}

.use-case p {
  margin: 0;
  color: #606266;
}

.summary-section {
  margin-top: 30px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.summary-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

.summary-card {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  height: 100%;
}

.summary-card h4 {
  margin-bottom: 12px;
  color: #606266;
}

.summary-card ul {
  padding-left: 20px;
  margin: 0;
  line-height: 1.8;
}
</style>
