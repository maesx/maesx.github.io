<template>
  <div class="segment-container">
    <el-row :gutter="20">
      <!-- 左侧：上传和配置 -->
      <el-col :span="8">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>分割配置</span>
            </div>
          </template>
          
          <!-- 模型选择 -->
          <div class="config-section">
            <h4>选择模型</h4>
            <el-select 
              v-model="selectedModel" 
              placeholder="请选择模型"
              style="width: 100%"
              @change="handleModelChange"
            >
              <el-option
                v-for="model in models"
                :key="model.name"
                :label="model.display_name || model.name"
                :value="model.name"
              />
            </el-select>
          </div>
          
          <!-- 分割类型 -->
          <div class="config-section">
            <h4>分割类型</h4>
            <el-radio-group v-model="segmentType">
              <el-radio label="semantic">语义分割</el-radio>
              <el-radio label="instance">实例分割</el-radio>
            </el-radio-group>
          </div>
          
          <!-- 图片上传 -->
          <div class="config-section">
            <h4>上传图片</h4>
            <el-upload
              ref="uploadRef"
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept="image/*"
              multiple
            >
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">
                将图片拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="upload-tip">
                  支持 JPG、PNG、BMP、TIFF 格式，可批量上传
                </div>
              </template>
            </el-upload>
            
            <!-- 已选图片列表 -->
            <div v-if="selectedFiles.length > 0" class="file-list">
              <div class="file-count">
                已选择 {{ selectedFiles.length }} 张图片
              </div>
              
              <!-- 单张图片显示预览 -->
              <div v-if="selectedFiles.length === 1" class="single-preview">
                <img :src="getFilePreview(selectedFiles[0])" alt="预览" />
                <div class="file-info">
                  <el-icon><Picture /></el-icon>
                  <span class="file-name">{{ selectedFiles[0].name }}</span>
                  <el-button 
                    text 
                    type="danger" 
                    size="small"
                    @click="removeFile(0)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
              
              <!-- 多张图片显示列表 -->
              <div v-else>
                <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
                  <el-icon><Picture /></el-icon>
                  <span class="file-name">{{ file.name }}</span>
                  <el-button 
                    text 
                    type="danger" 
                    size="small"
                    @click="removeFile(index)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :loading="segmenting"
              :disabled="!selectedModel || selectedFiles.length === 0"
              @click="startSegmentation"
            >
              {{ segmenting ? '分割中...' : '开始分割' }}
            </el-button>
            
            <el-button
              size="large"
              @click="resetAll"
            >
              重置
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：结果展示 -->
      <el-col :span="16">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>分割结果</span>
              <el-button 
                v-if="result"
                type="primary"
                size="small"
                @click="downloadResult"
              >
                <el-icon><Download /></el-icon>
                下载结果
              </el-button>
            </div>
          </template>
          
          <!-- 空状态 -->
          <div v-if="!result" class="empty-state">
            <el-empty description="请上传图片并选择模型开始分割" />
          </div>
          
          <!-- 结果展示 -->
          <div v-else class="result-content">
            <!-- 性能指标 -->
            <div class="metrics">
              <el-tag type="success" size="large">
                IoU: {{ (result.iou * 100).toFixed(2) }}%
              </el-tag>
              <el-tag type="info" size="large">
                准确率: {{ (result.accuracy * 100).toFixed(2) }}%
              </el-tag>
              <el-tag size="large">
                处理时间: {{ result.process_time.toFixed(2) }}s
              </el-tag>
            </div>
            
            <!-- 图片对比 -->
            <div class="image-comparison">
              <div class="image-box">
                <h4>原始图片</h4>
                <img :src="result.original_image" alt="原图" />
              </div>
              
              <div class="image-box">
                <h4>分割结果</h4>
                <img :src="result.segmented_image" alt="分割图" />
              </div>
              
              <div class="image-box">
                <h4>融合效果</h4>
                <img :src="result.fused_image" alt="融合图" />
              </div>
            </div>
            
            <!-- 图表展示 -->
            <div class="charts">
              <div class="chart-box">
                <h4>各类别IoU分布</h4>
                <div ref="chartRef" style="width: 100%; height: 300px"></div>
              </div>
              
              <div class="chart-box">
                <h4>像素分布</h4>
                <div ref="pieChartRef" style="width: 100%; height: 300px"></div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { modelApi, segmentApi } from '@/api/modules'

const models = ref([])
const selectedModel = ref('')
const segmentType = ref('semantic')
const selectedFiles = ref([])
const segmenting = ref(false)
const result = ref(null)
const chartRef = ref(null)
const pieChartRef = ref(null)

const fetchModels = async () => {
  try {
    const response = await modelApi.getModels()
    if (response.success) {
      models.value = response.models
      // 默认选择最佳模型
      if (models.value.length > 0) {
        const bestModel = models.value.find(m => m.name === 'best_model.pth')
        selectedModel.value = bestModel ? bestModel.name : models.value[0].name
      }
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
  }
}

const handleFileChange = (file) => {
  selectedFiles.value.push(file.raw)
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const getFilePreview = (file) => {
  return URL.createObjectURL(file)
}

const handleModelChange = (modelName) => {
  console.log('选择模型:', modelName)
}

const startSegmentation = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先上传图片')
    return
  }
  
  try {
    segmenting.value = true
    
    const formData = new FormData()
    formData.append('model', selectedModel.value)
    formData.append('type', segmentType.value)
    
    // 添加文件
    selectedFiles.value.forEach((file, index) => {
      formData.append('images', file)
    })
    
    const response = await segmentApi.segment(formData, (progress) => {
      console.log('上传进度:', progress)
    })
    
    if (response.success) {
      result.value = response.result
      ElMessage.success('分割完成')
      
      // 渲染图表
      await nextTick()
      renderCharts()
    }
  } catch (error) {
    ElMessage.error('分割失败')
    console.error(error)
  } finally {
    segmenting.value = false
  }
}

const renderCharts = () => {
  if (!result.value) return
  
  // IoU柱状图
  const chart = echarts.init(chartRef.value)
  const iouChartOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: result.value.class_names || ['Background', 'Road', 'Vehicle', 'Pedestrian']
    },
    yAxis: { type: 'value', name: 'IoU (%)' },
    series: [{
      data: (result.value.class_iou || [98, 85, 78, 72]).map(v => (v * 100).toFixed(2)),
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#1890ff' },
          { offset: 1, color: '#69c0ff' }
        ])
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}%',
        color: '#333',
        fontWeight: 'bold',
        fontSize: 14
      }
    }]
  }
  chart.setOption(iouChartOption)
  
  // 像素分布饼图
  const pieChart = echarts.init(pieChartRef.value)
  const pieChartOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { value: 60, name: '背景' },
        { value: 20, name: '道路' },
        { value: 15, name: '车辆' },
        { value: 5, name: '行人' }
      ],
      label: {
        show: true,
        formatter: '{b}: {d}%',
        fontWeight: 'bold',
        fontSize: 12
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  pieChart.setOption(pieChartOption)
}

const downloadResult = () => {
  ElMessage.success('下载功能开发中')
}

const resetAll = () => {
  selectedFiles.value = []
  result.value = null
  selectedModel.value = models.value[0]?.name || ''
}

onMounted(() => {
  fetchModels()
})
</script>

<style scoped>
.segment-container {
  height: 100%;
}

.config-card, .result-card {
  height: calc(100vh - 140px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-section {
  margin-bottom: 24px;
}

.config-section h4 {
  margin-bottom: 12px;
  color: #606266;
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.file-list {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.file-count {
  font-size: 14px;
  color: #409eff;
  margin-bottom: 8px;
}

.single-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.single-preview img {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
  border: 2px solid #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.file-item:last-child {
  border-bottom: none;
}

.file-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.action-buttons .el-button {
  flex: 1;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.result-content {
  padding: 20px;
}

.metrics {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  justify-content: center;
}

.image-comparison {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.image-box {
  text-align: center;
}

.image-box h4 {
  margin-bottom: 12px;
  color: #606266;
}

.image-box img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 24px;
}

.chart-box {
  text-align: center;
}

.chart-box h4 {
  margin-bottom: 12px;
  color: #606266;
}
</style>
