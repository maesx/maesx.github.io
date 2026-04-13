<template>
  <div class="segment-container">
    <el-row :gutter="20">
      <!-- 左侧：上传和配置 -->
      <el-col :span="8">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>分割配置</span>
              <el-button 
                type="primary" 
                size="small"
                @click="$router.push('/augmentation')"
              >
                <el-icon><MagicStick /></el-icon>
                高级功能
              </el-button>
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
            <el-radio-group v-model="segmentType" class="segment-type-options">
              <el-radio value="semantic" class="segment-type-item">
                <div class="segment-type-content">
                  <span class="segment-label">语义分割</span>
                </div>
              </el-radio>
              <el-radio value="instance" class="segment-type-item">
                <div class="segment-type-content">
                  <span class="segment-label">实例分割</span>
                </div>
              </el-radio>
            </el-radio-group>
            <div class="segment-type-desc">
              <span v-if="segmentType === 'semantic'">将识别图像中的不同类别区域</span>
              <span v-else-if="segmentType === 'instance'">将区分同一类别的不同实例个体</span>
            </div>
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
                将图片或文件夹拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="upload-tip">
                  支持 JPG、PNG、BMP、TIFF 格式，支持批量上传或上传文件夹<br>
                  批量上传总大小不超过 50MB
                </div>
              </template>
            </el-upload>
            
            <!-- 已选图片列表 -->
            <div v-if="selectedFiles.length > 0" class="file-list">
              <div class="file-count">
                已选择 {{ selectedFiles.length }} 张图片
              </div>
              
              <!-- 上传进度条 -->
              <div v-if="uploading" class="upload-progress">
                <el-progress 
                  :percentage="uploadProgress" 
                  :status="uploadProgress === 100 ? 'success' : ''"
                  :stroke-width="8"
                />
                <div class="progress-text">{{ uploadStatusText }}</div>
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
              <div style="display: flex; gap: 10px;">
                <!-- 单张结果下载 -->
                <el-button 
                  v-if="result && !batchResult"
                  type="primary"
                  size="small"
                  @click="downloadResult"
                >
                  <el-icon><Download /></el-icon>
                  下载结果
                </el-button>
                
                <!-- 批量结果ZIP下载 -->
                <el-button 
                  v-if="batchResult && batchResult.zip_file"
                  type="primary"
                  size="small"
                  @click="downloadBatchZip"
                >
                  <el-icon><Download /></el-icon>
                  下载全部结果（ZIP）
                </el-button>
                
                <!-- 清空批量结果 -->
                <el-button
                  v-if="batchResult"
                  size="small"
                  @click="clearBatchResult"
                >
                  清空结果
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 空状态 -->
          <div v-if="!result && !batchResult" class="empty-state">
            <el-empty description="请上传图片并选择模型开始分割" />
          </div>
          
          <!-- 单张结果展示 -->
          <div v-else-if="result && !batchResult" class="result-content">
            <!-- 性能指标 -->
            <div class="metrics">
              <el-tag :type="result.segment_type === 'instance' ? 'warning' : 'primary'" size="large">
                {{ result.segment_type === 'instance' ? '实例分割' : '语义分割' }}
              </el-tag>
              <el-tag type="success" size="large">
                IoU: {{ (result.iou * 100).toFixed(2) }}%
              </el-tag>
              <el-tag type="info" size="large">
                准确率: {{ (result.accuracy * 100).toFixed(2) }}%
              </el-tag>
              <el-tag size="large">
                处理时间: {{ result.process_time.toFixed(2) }}s
              </el-tag>
              <el-tag v-if="result.segment_type === 'instance'" type="warning" size="large">
                检测实例: {{ result.instance_count || 0 }} 个
              </el-tag>
            </div>
            
            <!-- 图像对比滑块 -->
            <div class="compare-section">
              <h4 style="margin-bottom: 16px;">原图 vs 分割结果对比</h4>
              <ImageCompare 
                :original-image="result.original_image"
                :result-image="result.segmented_image"
                style="height: 400px; margin-bottom: 20px;"
              />
            </div>
            
            <!-- 详细图片展示 -->
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
            
            <!-- 实例分割结果显示 -->
            <div v-if="result.segment_type === 'instance' && result.bbox_image" class="instance-result">
              <div class="image-box" style="width: 100%;">
                <h4>实例检测结果（带边界框）</h4>
                <img :src="result.bbox_image" alt="实例检测图" style="max-height: 400px;" />
              </div>
            </div>
            
            <!-- 实例信息列表 -->
            <div v-if="result.segment_type === 'instance' && result.instance_info && result.instance_info.length > 0" class="instance-info">
              <h4>检测到的实例详情</h4>
              <el-table :data="result.instance_info" style="width: 100%" max-height="300">
                <el-table-column prop="id" label="实例ID" width="100" />
                <el-table-column prop="class_name" label="类别" width="120">
                  <template #default="scope">
                    <el-tag :type="getTagType(scope.row.class_id)">
                      {{ scope.row.class_name }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="area" label="面积（像素）" width="120">
                  <template #default="scope">
                    {{ scope.row.area.toLocaleString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="bbox" label="边界框">
                  <template #default="scope">
                    [{{ scope.row.bbox.join(', ') }}]
                  </template>
                </el-table-column>
                <el-table-column label="颜色" width="80">
                  <template #default="scope">
                    <div 
                      class="color-preview" 
                      :style="{ backgroundColor: `rgb(${scope.row.color.join(',')})` }"
                    ></div>
                  </template>
                </el-table-column>
              </el-table>
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
          
          <!-- 批量结果展示 -->
          <div v-else-if="batchResult" class="batch-result-content">
            <!-- 批量结果统计 -->
            <div class="batch-summary">
              <el-alert
                :title="batchResult.message"
                type="success"
                :closable="false"
                show-icon
                style="margin-bottom: 16px;"
              />
              
              <div class="batch-stats">
                <el-tag size="large" type="info">总数: {{ batchResult.total_count }}</el-tag>
                <el-tag size="large" type="success">成功: {{ batchResult.success_count }}</el-tag>
                <el-tag size="large" type="danger" v-if="batchResult.failed_count > 0">
                  失败: {{ batchResult.failed_count }}
                </el-tag>
              </div>
              
              <!-- 失败文件列表 -->
              <el-alert
                v-if="batchResult.failed_count > 0"
                :title="batchResult.warning"
                type="warning"
                :closable="false"
                show-icon
                style="margin-top: 12px;"
              >
                <ul style="margin: 8px 0 0 20px; padding: 0;">
                  <li v-for="(failed, idx) in batchResult.failed_files" :key="idx">
                    {{ failed.filename }}: {{ failed.error }}
                  </li>
                </ul>
              </el-alert>
            </div>
            
            <!-- 直接展示模式（<=3张） -->
            <div v-if="batchResult.display_mode === 'direct'" class="batch-direct-results">
              <h4 style="margin-bottom: 16px;">分割结果</h4>
              <div v-for="(item, index) in batchResult.results" :key="index" class="batch-result-item">
                <el-divider content-position="left">
                  <el-tag>{{ item.original_filename }}</el-tag>
                </el-divider>
                
                <!-- 性能指标 -->
                <div class="metrics">
                  <el-tag :type="item.segment_type === 'instance' ? 'warning' : 'primary'">
                    {{ item.segment_type === 'instance' ? '实例分割' : '语义分割' }}
                  </el-tag>
                  <el-tag type="success">IoU: {{ (item.iou * 100).toFixed(2) }}%</el-tag>
                  <el-tag type="info">准确率: {{ (item.accuracy * 100).toFixed(2) }}%</el-tag>
                  <el-tag>处理时间: {{ item.process_time.toFixed(2) }}s</el-tag>
                </div>
                
                <!-- 图片对比 -->
                <div class="image-comparison">
                  <div class="image-box">
                    <h4>原始图片</h4>
                    <img :src="item.original_image" alt="原图" />
                  </div>
                  <div class="image-box">
                    <h4>分割结果</h4>
                    <img :src="item.segmented_image" alt="分割图" />
                  </div>
                  <div class="image-box">
                    <h4>融合效果</h4>
                    <img :src="item.fused_image" alt="融合图" />
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 预览模式（>3张） -->
            <div v-else-if="batchResult.display_mode === 'preview'" class="batch-preview-results">
              <el-alert
                title="此处展示前3张分割结果，其余结果请下载ZIP文件查看"
                type="info"
                :closable="false"
                show-icon
                style="margin-bottom: 20px;"
              />
              
              <div v-for="(item, index) in batchResult.preview_results" :key="index" class="batch-result-item">
                <el-divider content-position="left">
                  <el-tag>{{ item.original_filename }}</el-tag>
                </el-divider>
                
                <!-- 性能指标 -->
                <div class="metrics">
                  <el-tag :type="item.segment_type === 'instance' ? 'warning' : 'primary'">
                    {{ item.segment_type === 'instance' ? '实例分割' : '语义分割' }}
                  </el-tag>
                  <el-tag type="success">IoU: {{ (item.iou * 100).toFixed(2) }}%</el-tag>
                  <el-tag type="info">准确率: {{ (item.accuracy * 100).toFixed(2) }}%</el-tag>
                  <el-tag>处理时间: {{ item.process_time.toFixed(2) }}s</el-tag>
                </div>
                
                <!-- 图片对比 -->
                <div class="image-comparison">
                  <div class="image-box">
                    <h4>原始图片</h4>
                    <img :src="item.original_image" alt="原图" />
                  </div>
                  <div class="image-box">
                    <h4>分割结果</h4>
                    <img :src="item.segmented_image" alt="分割图" />
                  </div>
                  <div class="image-box">
                    <h4>融合效果</h4>
                    <img :src="item.fused_image" alt="融合图" />
                  </div>
                </div>
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
import { MagicStick } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { modelApi, segmentApi } from '@/api/modules'
import ImageCompare from '@/components/ImageCompare.vue'

const models = ref([])
const selectedModel = ref('')
const segmentType = ref('semantic')
const selectedFiles = ref([])
const segmenting = ref(false)
const result = ref(null)
const batchResult = ref(null)
const chartRef = ref(null)
const pieChartRef = ref(null)

// 上传进度相关
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatusText = ref('')

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
  
  // 显示当前使用的分割类型
  const typeText = segmentType.value === 'semantic' ? '语义分割' : '实例分割'
  const fileCountText = selectedFiles.value.length === 1 ? '单张图片' : `${selectedFiles.value.length}张图片`
  
  ElMessage.info(`正在使用 ${typeText} 模式处理 ${fileCountText}`)
  
  try {
    segmenting.value = true
    uploading.value = true
    uploadProgress.value = 0
    uploadStatusText.value = '准备上传...'
    
    const formData = new FormData()
    formData.append('model', selectedModel.value)
    formData.append('type', segmentType.value)
    
    // 添加文件
    selectedFiles.value.forEach((file, index) => {
      formData.append('images', file)
    })
    
    // 进度回调
    const onProgress = (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      uploadProgress.value = percentCompleted
      uploadStatusText.value = percentCompleted < 100 ? `上传中 ${percentCompleted}%` : '上传完成，正在处理...'
    }
    
    // 根据文件数量调用不同的API
    if (selectedFiles.value.length === 1) {
      // 单张图片分割
      const response = await segmentApi.segment(formData, onProgress)
      
      if (response.success) {
        result.value = response.result
        batchResult.value = null  // 清空批量结果
        uploadStatusText.value = '分割完成'
        ElMessage.success(`${typeText}完成`)
        
        // 渲染图表
        await nextTick()
        renderCharts()
      }
    } else {
      // 批量分割
      const response = await segmentApi.batchSegment(formData, onProgress)
      
      if (response.success) {
        batchResult.value = response
        result.value = null  // 清空单张结果
        uploadStatusText.value = '批量分割完成'
        ElMessage.success('批量分割完成')
      }
    }
  } catch (error) {
    ElMessage.error('分割失败')
    uploadStatusText.value = '上传失败'
    console.error(error)
  } finally {
    segmenting.value = false
    setTimeout(() => {
      uploading.value = false
    }, 1000) // 延迟1秒隐藏进度条
  }
}

const renderCharts = () => {
  if (!result.value) return
  
  // IoU柱状图
  const chart = echarts.init(chartRef.value)
  const classNames = result.value.class_names || ['Background', 'Road', 'Vehicle', 'Pedestrian']
  const classIou = result.value.class_iou || [98, 85, 78, 72]
  
  // 如果使用默认值，输出警告
  if (!result.value.class_names || !result.value.class_iou) {
    console.warn('[警告] 使用默认的类别名称或 IoU 数据，后端可能未正确返回数据')
  }
  
  const iouChartOption = {
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 12
      }
    },
    yAxis: { 
      type: 'value', 
      name: 'IoU (%)',
      min: 0,
      max: 100
    },
    series: [{
      data: classIou.map(v => (v * 100).toFixed(2)),
      type: 'bar',
      barWidth: '50%',
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
        fontSize: 12
      }
    }]
  }
  chart.setOption(iouChartOption)
  
  // 像素分布饼图 - 使用后端返回的数据
  const pieChart = echarts.init(pieChartRef.value)
  const pixelDistribution = result.value.pixel_distribution || [60, 20, 15, 5]
  
  // 如果使用默认值，输出警告
  if (!result.value.pixel_distribution) {
    console.warn('[警告] 使用默认的像素分布数据，后端可能未正确返回数据')
  }
  
  const pieChartOption = {
    tooltip: { 
      trigger: 'item',
      formatter: '{b}: {d}%'
    },
    legend: { 
      orient: 'horizontal',
      bottom: '5%',
      itemWidth: 12,
      itemHeight: 12,
      textStyle: { fontSize: 11 }
    },
    series: [{
      type: 'pie',
      radius: ['30%', '55%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      data: classNames.map((name, idx) => ({
        value: pixelDistribution[idx],
        name: name
      })),
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 11,
        lineHeight: 16
      },
      labelLine: {
        length: 10,
        length2: 10
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

const getTagType = (classId) => {
  const types = ['', 'success', 'warning', 'danger', 'info']
  return types[classId % types.length] || 'info'
}

const downloadResult = () => {
  if (!result.value) return
  
  try {
    // 创建一个临时的下载链接
    const link = document.createElement('a')
    link.href = result.value.segmented_image
    link.download = `segmentation_result_${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('结果已下载')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

const resetAll = () => {
  selectedFiles.value = []
  result.value = null
  batchResult.value = null
  selectedModel.value = models.value[0]?.name || ''
  segmentType.value = 'semantic'
}

const downloadBatchZip = () => {
  if (!batchResult.value || !batchResult.value.zip_file) return
  
  try {
    // 创建下载链接
    const link = document.createElement('a')
    link.href = batchResult.value.zip_file
    link.download = `segmentation_results_${Date.now()}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('ZIP文件下载中...')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

const clearBatchResult = () => {
  batchResult.value = null
  ElMessage.success('已清空批量结果')
}

onMounted(() => {
  fetchModels()
  
  // 检查是否有从增强页面传来的图片
  const augmentedImage = sessionStorage.getItem('augmentedImage')
  const augmentedImageType = sessionStorage.getItem('augmentedImageType')
  
  if (augmentedImage) {
    try {
      // 将base64转换为File对象
      fetch(augmentedImage)
        .then(res => res.blob())
        .then(blob => {
          const file = new File(
            [blob], 
            `augmented_image_${Date.now()}.png`, 
            { type: 'image/png' }
          )
          selectedFiles.value = [file]
          
          ElMessage.success(`已加载增强图片（${augmentedImageType || '未知类型'}），请选择模型进行分割`)
          
          // 清除sessionStorage
          sessionStorage.removeItem('augmentedImage')
          sessionStorage.removeItem('augmentedImageType')
        })
        .catch(error => {
          console.error('加载增强图片失败:', error)
          ElMessage.error('加载增强图片失败')
        })
    } catch (error) {
      console.error('处理增强图片失败:', error)
    }
  }
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
  font-weight: 600;
}

/* 分割类型选择样式 - 简洁列表形式 */
.segment-type-options {
  width: 100% !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
  margin-bottom: 12px !important;
}

:deep(.segment-type-options) {
  width: 100% !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
  margin-bottom: 12px !important;
}

.segment-type-item {
  position: relative !important;
  margin: 0 !important;
  flex: 1 !important;
  min-width: 100px !important;
  box-sizing: border-box !important;
  display: block !important;
}

:deep(.segment-type-item .el-radio__input) {
  display: none !important;
}

:deep(.segment-type-item .el-radio__label) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 !important;
  width: 100% !important;
  height: auto !important;
}

.segment-type-content {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  padding: 12px 20px !important;
  border: 1px solid #dcdfe6 !important;
  border-radius: 4px !important;
  background: #ffffff !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  box-sizing: border-box !important;
}

.segment-type-content:hover {
  border-color: #1890ff !important;
  color: #1890ff !important;
}

:deep(.segment-type-item.is-checked .segment-type-content) {
  border-color: #1890ff !important;
  background: #1890ff !important;
  color: #ffffff !important;
}

.segment-label {
  font-size: 14px !important;
  font-weight: 500 !important;
  text-align: center !important;
}

:deep(.segment-type-item.is-checked .segment-label) {
  color: #ffffff !important;
}

.segment-type-desc {
  margin-top: 8px;
  padding-left: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.6;
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

.upload-progress {
  margin: 16px 0;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.progress-text {
  margin-top: 8px;
  text-align: center;
  font-size: 13px;
  color: #606266;
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

.compare-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.compare-section h4 {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
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

/* 批量结果样式 */
.batch-result-content {
  padding: 20px;
}

.batch-summary {
  margin-bottom: 24px;
}

.batch-stats {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 16px 0;
}

.batch-direct-results,
.batch-preview-results {
  margin-top: 20px;
}

.batch-result-item {
  margin-bottom: 24px;
}

.batch-result-item .image-comparison {
  margin-top: 12px;
}
</style>