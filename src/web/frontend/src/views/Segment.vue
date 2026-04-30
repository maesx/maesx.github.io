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
              
              <!-- 单张图片时显示预览，多张图片时不显示预览 -->
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
              
              <!-- 多张图片显示文件列表 -->
              <div v-else class="multi-files-list">
                <div v-for="(file, index) in selectedFiles.slice(0, 5)" :key="index" class="file-item">
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
                <div v-if="selectedFiles.length > 5" class="more-files">
                  <el-tag type="info" size="small">
                    还有 {{ selectedFiles.length - 5 }} 张图片
                  </el-tag>
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
                  v-if="batchResult && batchResult.download_available"
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
            
            <!-- 实例分割结果显示 - 已隐藏边界框图 -->
            <!-- 实例信息列表 - 已隐藏详情表格 -->
            
            </div>
          
          <!-- 批量结果展示 -->
          <div v-else-if="batchResult" class="batch-result-content">
            <!-- 批量结果统计 -->
            <div class="batch-summary">
              <el-alert
                :title="`批量分割完成：共 ${batchResult.total_count} 张，成功 ${batchResult.processed_count} 张`"
                type="success"
                :closable="false"
                show-icon
                style="margin-bottom: 16px;"
              />
              
              <div class="batch-stats">
                <el-tag size="large" type="info">总数: {{ batchResult.total_count }}</el-tag>
                <el-tag size="large" type="success">成功: {{ batchResult.processed_count }}</el-tag>
                <el-tag size="large" type="danger" v-if="batchResult.failed_count > 0">
                  失败: {{ batchResult.failed_count }}
                </el-tag>
              </div>
            </div>
            
            <!-- 直接展示模式（<=3张） -->
            <div v-if="batchResult.display_mode === 'direct'" class="batch-direct-results">
              <h4 style="margin-bottom: 16px;">分割结果</h4>
              <div v-for="(item, index) in batchResult.results" :key="index" class="batch-result-item">
                <el-divider content-position="left">
                  <el-tag>{{ item.filename }}</el-tag>
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
                
                <!-- 图像对比滑块 -->
                <div class="compare-section">
                  <h4 style="margin-bottom: 16px;">原图 vs 分割结果对比</h4>
                  <ImageCompare 
                    :original-image="item.original_image"
                    :result-image="item.segmented_image"
                    style="height: 400px; margin-bottom: 20px;"
                  />
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
                  <el-tag>{{ item.filename }}</el-tag>
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
                
                <!-- 图像对比滑块 -->
                <div class="compare-section">
                  <h4 style="margin-bottom: 16px;">原图 vs 分割结果对比</h4>
                  <ImageCompare 
                    :original-image="item.original_image"
                    :result-image="item.segmented_image"
                    style="height: 400px; margin-bottom: 20px;"
                  />
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
              
              <!-- 提示剩余图片 -->
              <div v-if="batchResult.total_count > 3" class="remaining-hint">
                <el-icon><InfoFilled /></el-icon>
                <span>还有 {{ batchResult.total_count - 3 }} 张图片的分割结果，请点击上方"下载全部结果"按钮获取</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, InfoFilled } from '@element-plus/icons-vue'
import { modelApi, segmentApi } from '@/api/modules'
import ImageCompare from '@/components/ImageCompare.vue'

const models = ref([])
const selectedModel = ref('')
const segmentType = ref('semantic')
const selectedFiles = ref([])
const segmenting = ref(false)
const result = ref(null)
const batchResult = ref(null)

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
        // 后端返回的name已经去除了.pth后缀
        const bestModel = models.value.find(m => m.name === 'best_model' || m.name === 'best_model.pth')
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

const downloadBatchZip = async () => {
  if (!batchResult.value || !batchResult.value.task_id) return
  
  try {
    ElMessage.info('正在准备下载...')
    
    // 使用 API 下载
    const response = await fetch(`/api/segment/download/${batchResult.value.task_id}`)
    
    if (!response.ok) {
      throw new Error('下载失败')
    }
    
    // 获取 blob
    const blob = await response.blob()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `segmentation_results_${batchResult.value.task_id.slice(0, 8)}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载完成')
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

.remaining-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
  color: #1890ff;
  font-size: 14px;
  margin-top: 20px;
}

.multi-files-tip {
  margin-top: 8px;
  text-align: center;
}

.multi-files-list {
  background: white;
  border-radius: 8px;
  padding: 12px;
  margin-top: 8px;
}

.multi-files-list .file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
}

.multi-files-list .file-item:last-child {
  border-bottom: none;
}

.more-files {
  margin-top: 8px;
  text-align: center;
  padding: 8px;
}
</style>