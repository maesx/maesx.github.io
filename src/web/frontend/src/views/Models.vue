<template>
  <div class="models-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>模型列表</span>
            </div>
          </template>
          
          <el-table :data="models" stripe>
            <el-table-column prop="name" label="模型名称" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="scope">
                <el-tag>{{ scope.row.type || 'Semantic' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="iou" label="IoU" width="100">
              <template #default="scope">
                <span v-if="scope.row.iou">{{ (scope.row.iou * 100).toFixed(2) }}%</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="大小" width="120">
              <template #default="scope">
                {{ (scope.row.size / (1024 * 1024)).toFixed(2) }} MB
              </template>
            </el-table-column>
            <el-table-column prop="modified" label="更新时间" width="180" />
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>上传模型</span>
          </template>
          
          <el-upload
            drag
            action="/api/models/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            accept=".pth,.pt"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              将模型文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="upload-tip">
                支持 .pth、.pt 格式的 PyTorch 模型文件
              </div>
            </template>
          </el-upload>
          
          <div class="model-info">
            <h4>模型说明</h4>
            <ul>
              <li>支持 PyTorch 模型文件</li>
              <li>模型会自动验证和解析</li>
              <li>请确保模型与系统兼容</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi } from '@/api/modules'

const models = ref([])

const fetchModels = async () => {
  try {
    const response = await modelApi.getModels()
    if (response.success) {
      models.value = response.models
    }
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  }
}

const handleUploadSuccess = (response) => {
  if (response.success) {
    ElMessage.success('模型上传成功')
    fetchModels()
  }
}

const handleUploadError = () => {
  ElMessage.error('模型上传失败')
}

onMounted(() => {
  fetchModels()
})
</script>

<style scoped>
.models-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.model-info {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.model-info h4 {
  margin-bottom: 12px;
  color: #606266;
}

.model-info ul {
  padding-left: 20px;
  line-height: 1.8;
  color: #909399;
  font-size: 13px;
}
</style>
