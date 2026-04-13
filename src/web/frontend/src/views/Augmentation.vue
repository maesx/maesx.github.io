<template>
  <div class="augmentation-container">
    <el-row :gutter="20">
      <!-- 左侧：配置和上传 -->
      <el-col :span="8">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>数据增强配置</span>
            </div>
          </template>
          
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
                  支持 JPG、PNG、BMP、TIFF 格式<br>
                  支持多选图片
                </div>
              </template>
            </el-upload>
            
            <!-- 已选图片列表 -->
            <div v-if="selectedFiles.length > 0" class="file-list">
              <div class="file-count">
                已选择 {{ selectedFiles.length }} 张图片
              </div>
              
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
          
          <!-- 增强方式选择 -->
          <div class="config-section">
            <h4>选择增强方式</h4>
            <el-checkbox-group v-model="selectedAugmentations" class="augmentation-options">
              <!-- 基础增强 -->
              <div class="augmentation-group">
                <div class="group-header">
                  <el-icon><Setting /></el-icon>
                  <span class="group-title">基础增强</span>
                </div>
                <div class="checkbox-list">
                  <el-checkbox label="rotate" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><RefreshRight /></el-icon>
                      <span>旋转</span>
                    </div>
                  </el-checkbox>
                  <el-checkbox label="flip" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><Switch /></el-icon>
                      <span>翻转</span>
                    </div>
                  </el-checkbox>
                  <el-checkbox label="scale" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><ZoomIn /></el-icon>
                      <span>缩放</span>
                    </div>
                  </el-checkbox>
                  <el-checkbox label="crop" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><Crop /></el-icon>
                      <span>裁剪</span>
                    </div>
                  </el-checkbox>
                </div>
              </div>
              
              <!-- 高级增强 -->
              <div class="augmentation-group">
                <div class="group-header">
                  <el-icon><MagicStick /></el-icon>
                  <span class="group-title">高级增强</span>
                </div>
                <div class="checkbox-list">
                  <el-checkbox label="color" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><Brush /></el-icon>
                      <span>颜色调整</span>
                    </div>
                  </el-checkbox>
                  <el-checkbox label="noise" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><Grid /></el-icon>
                      <span>噪声</span>
                    </div>
                  </el-checkbox>
                  <el-checkbox label="blur" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><View /></el-icon>
                      <span>模糊</span>
                    </div>
                  </el-checkbox>
                  <el-checkbox label="brightness" class="custom-checkbox">
                    <div class="checkbox-content">
                      <el-icon class="checkbox-icon"><Sunny /></el-icon>
                      <span>亮度对比度</span>
                    </div>
                  </el-checkbox>
                </div>
              </div>
            </el-checkbox-group>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :loading="augmenting"
              :disabled="selectedFiles.length === 0 || selectedAugmentations.length === 0"
              @click="startAugmentation"
            >
              {{ augmenting ? '生成中...' : '生成增强效果' }}
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
              <span>增强效果预览</span>
              <div style="display: flex; gap: 10px;">
                <!-- ZIP下载按钮 -->
                <el-button 
                  v-if="augmentationResults && augmentationResults.length > 0"
                  type="primary"
                  size="small"
                  @click="downloadAllResults"
                >
                  <el-icon><Download /></el-icon>
                  下载全部结果（ZIP）
                </el-button>
                
                <!-- 清空结果 -->
                <el-button
                  v-if="augmentationResults && augmentationResults.length > 0"
                  size="small"
                  @click="clearResults"
                >
                  清空结果
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 空状态 -->
          <div v-if="!augmentationResults || augmentationResults.length === 0" class="empty-state">
            <el-empty description="请上传图片并选择增强方式" />
          </div>
          
          <!-- 增强结果展示 -->
          <div v-else class="results-container">
            <div v-for="(resultGroup, index) in augmentationResults" :key="index" class="result-group">
              <el-divider content-position="left">
                <el-tag>{{ resultGroup.original_filename }}</el-tag>
              </el-divider>
              
              <!-- 原图 -->
              <div class="original-image-section">
                <h4>原始图片</h4>
                <img :src="resultGroup.original_image" alt="原图" class="preview-image" />
              </div>
              
              <!-- 增强效果对比 -->
              <div class="augmented-images-section">
                <h4>增强效果（随机生成 2-3 种）</h4>
                <el-row :gutter="16">
                  <el-col 
                    v-for="(aug, augIndex) in resultGroup.augmented_images" 
                    :key="augIndex" 
                    :span="8"
                  >
                    <div class="augmented-item">
                      <div class="aug-info">
                        <el-tag type="success" size="small">{{ aug.augmentation_type }}</el-tag>
                      </div>
                      <img :src="aug.image" :alt="`增强${augIndex + 1}`" class="preview-image" />
                      <div class="aug-actions">
                        <el-button 
                          size="small" 
                          @click="downloadSingleImage(aug)"
                        >
                          <el-icon><Download /></el-icon>
                          下载
                        </el-button>
                        <el-button 
                          size="small" 
                          type="primary"
                          @click="sendToSegment(aug)"
                        >
                          <el-icon><Upload /></el-icon>
                          转入分割
                        </el-button>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { augmentationApi } from '@/api/modules'

const router = useRouter()
const selectedFiles = ref([])
const selectedAugmentations = ref([])
const augmenting = ref(false)
const augmentationResults = ref([])

const handleFileChange = (file) => {
  selectedFiles.value.push(file.raw)
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const startAugmentation = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先上传图片')
    return
  }
  
  if (selectedAugmentations.value.length === 0) {
    ElMessage.warning('请至少选择一种增强方式')
    return
  }
  
  try {
    augmenting.value = true
    
    const formData = new FormData()
    formData.append('augmentations', JSON.stringify(selectedAugmentations.value))
    
    // 添加文件
    selectedFiles.value.forEach((file, index) => {
      formData.append('images', file)
    })
    
    const response = await augmentationApi.preview(formData)
    
    if (response.success) {
      augmentationResults.value = response.results
      ElMessage.success(`成功生成 ${response.total_count} 个增强效果`)
    } else {
      ElMessage.error(response.error || '增强失败')
    }
  } catch (error) {
    ElMessage.error('增强失败')
    console.error(error)
  } finally {
    augmenting.value = false
  }
}

const resetAll = () => {
  selectedFiles.value = []
  selectedAugmentations.value = []
  augmentationResults.value = []
}

const clearResults = () => {
  augmentationResults.value = []
}

const downloadAllResults = async () => {
  try {
    ElMessage.info('正在打包下载...')
    
    // 调用后端接口下载ZIP
    const response = await augmentationApi.downloadZip()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response], { type: 'application/zip' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `augmentation_results_${Date.now()}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
    console.error(error)
  }
}

const downloadSingleImage = (aug) => {
  try {
    // 从base64创建下载链接
    const link = document.createElement('a')
    link.href = aug.image
    link.download = `augmented_${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
    console.error(error)
  }
}

const sendToSegment = (aug) => {
  try {
    // 将增强后的图片数据存储到sessionStorage
    sessionStorage.setItem('augmentedImage', aug.image)
    sessionStorage.setItem('augmentedImageType', aug.augmentation_type)
    
    ElMessage.success('已转入分割页面，请选择模型进行分割')
    
    // 跳转到分割页面
    router.push('/segment')
  } catch (error) {
    ElMessage.error('转入失败')
    console.error(error)
  }
}
</script>

<style scoped>
.augmentation-container {
  padding: 0;
}

.config-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-section {
  margin-bottom: 24px;
  padding: 0;
}

.config-section h4 {
  margin-bottom: 12px;
  color: #303133;
  padding-left: 0;
}

.upload-area {
  width: 100%;
  margin-bottom: 12px;
}

:deep(.el-upload-dragger) {
  padding: 30px;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-text em {
  color: #1890ff;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.file-list {
  margin-top: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.file-count {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: bold;
}

.single-preview {
  margin-top: 12px;
}

.single-preview img {
  width: 100%;
  max-height: 150px;
  object-fit: contain;
  border-radius: 4px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-name {
  flex: 1;
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.augmentation-options {
  width: 100%;
}

.augmentation-group {
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  width: 100%;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #1890ff;
}

.group-header .el-icon {
  font-size: 18px;
  color: #1890ff;
}

.group-title {
  font-size: 14px;
  color: #303133;
  font-weight: bold;
}

.checkbox-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
}

.custom-checkbox {
  margin: 0 !important;
  height: auto !important;
  width: 100%;
}

:deep(.custom-checkbox .el-checkbox__input) {
  display: none;
}

:deep(.custom-checkbox .el-checkbox__label) {
  padding-left: 0;
  width: 100%;
}

.checkbox-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 12px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
  background: #fff;
  width: 100%;
  min-height: 90px;
}

.checkbox-content:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
  transform: translateY(-2px);
}

:deep(.custom-checkbox.is-checked .checkbox-content) {
  border-color: #1890ff;
  background: linear-gradient(135deg, #e6f7ff 0%, #fff 100%);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

:deep(.custom-checkbox.is-checked .checkbox-content::before) {
  content: '✓';
  position: absolute;
  top: 8px;
  right: 8px;
  color: #1890ff;
  font-weight: bold;
  font-size: 18px;
}

.custom-checkbox {
  position: relative;
}

.checkbox-icon {
  font-size: 28px;
  color: #606266;
  margin-bottom: 8px;
  transition: all 0.3s;
}

:deep(.custom-checkbox.is-checked .checkbox-icon) {
  color: #1890ff;
  transform: scale(1.15);
}

.checkbox-content span {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons .el-button {
  flex: 1;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.results-container {
  padding: 20px;
}

.result-group {
  margin-bottom: 32px;
}

.result-group:last-child {
  margin-bottom: 0;
}

.original-image-section,
.augmented-images-section {
  margin-bottom: 16px;
}

.original-image-section h4,
.augmented-images-section h4 {
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}

.preview-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.augmented-item {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e4e7ed;
}

.aug-info {
  margin-bottom: 8px;
}

.augmented-item .preview-image {
  margin-bottom: 8px;
}

.aug-actions {
  text-align: center;
}
</style>
