<template>
  <div class="models-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>模型列表</span>
              <el-button
                type="primary"
                size="small"
                @click="fetchModels"
                :icon="Refresh"
              >
                刷新
              </el-button>
            </div>
          </template>

          <el-table :data="models" stripe v-loading="loading">
            <el-table-column prop="name" label="模型名称" min-width="150">
              <template #default="scope">
                <span>{{ scope.row.name }}</span>
                <el-tag v-if="scope.row.is_default" type="warning" size="small" style="margin-left: 8px">
                  默认
                </el-tag>
              </template>
            </el-table-column>
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
                {{ scope.row.size_mb ? scope.row.size_mb.toFixed(2) + ' MB' : (scope.row.size && typeof scope.row.size === 'number' ? (scope.row.size / (1024 * 1024)).toFixed(2) + ' MB' : scope.row.size || '-') }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="更新时间" width="180" />
            <el-table-column label="操作" width="100" v-if="isAdmin">
              <template #default="scope">
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  @click="handleDelete(scope.row)"
                  :disabled="scope.row.is_default"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8" v-if="isAdmin">
        <el-card>
          <template #header>
            <span>上传模型</span>
          </template>

          <el-form :model="uploadForm" label-width="80px" class="upload-form">
            <el-form-item label="模型名称">
              <el-input
                v-model="uploadForm.modelName"
                placeholder="留空则使用文件名"
                :disabled="uploading"
              />
            </el-form-item>
          </el-form>

          <el-upload
            ref="uploadRef"
            drag
            action="/api/models/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :on-progress="handleUploadProgress"
            :before-upload="beforeUpload"
            :data="uploadData"
            accept=".pth,.pt"
            :disabled="uploading"
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

          <el-progress
            v-if="uploading"
            :percentage="uploadProgress"
            :status="uploadProgress === 100 ? 'success' : ''"
            class="upload-progress"
          />

          <div class="model-info">
            <h4>模型说明</h4>
            <ul>
              <li>支持 PyTorch 模型文件</li>
              <li>模型会自动验证和解析</li>
              <li>请确保模型与系统兼容</li>
              <li>上传的模型可在列表中删除</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>确定要删除模型 <strong>{{ modelToDelete?.name }}</strong> 吗？</p>
      <p style="color: #909399; font-size: 13px;">此操作不可恢复。</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleting">
          确认删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Refresh, UploadFilled } from '@element-plus/icons-vue'
import { modelApi } from '@/api/modules'

const models = ref([])
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadRef = ref(null)

// 上传表单
const uploadForm = ref({
  modelName: ''
})

// 计算上传时的额外数据
const uploadData = computed(() => ({
  model_name: uploadForm.value.modelName || ''
}))

// 删除相关
const deleteDialogVisible = ref(false)
const modelToDelete = ref(null)
const deleting = ref(false)

// 检查是否为管理员（从localStorage获取用户信息）
const isAdmin = computed(() => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      return user.role === 'admin'
    }
  } catch (e) {
    console.error('获取用户信息失败:', e)
  }
  return false
})

const fetchModels = async () => {
  loading.value = true
  try {
    const response = await modelApi.getModels()
    if (response.success) {
      // 标记默认模型
      models.value = response.models.map(m => ({
        ...m,
        is_default: isDefaultModel(m.name)
      }))
    }
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  } finally {
    loading.value = false
  }
}

const isDefaultModel = (modelName) => {
  const defaultNames = ['best_model']
  return defaultNames.some(name =>
    modelName === name || modelName.startsWith(`${name}_`)
  )
}

const beforeUpload = (file) => {
  uploading.value = true
  uploadProgress.value = 0
  return true
}

const handleUploadProgress = (event) => {
  if (event.percent) {
    uploadProgress.value = Math.round(event.percent)
  }
}

const handleUploadSuccess = (response) => {
  uploading.value = false
  uploadProgress.value = 100
  if (response.success) {
    ElMessage.success('模型上传成功')
    uploadForm.value.modelName = ''
    fetchModels()
  } else {
    ElMessage.error(response.error || '模型上传失败')
  }
}

const handleUploadError = (error) => {
  uploading.value = false
  uploadProgress.value = 0
  ElMessage.error('模型上传失败')
}

const handleDelete = (model) => {
  if (model.is_default) {
    ElMessage.warning('系统默认模型不允许删除')
    return
  }
  modelToDelete.value = model
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!modelToDelete.value) return

  deleting.value = true
  try {
    const response = await modelApi.deleteModel(modelToDelete.value.name)
    if (response.success) {
      ElMessage.success('模型删除成功')
      deleteDialogVisible.value = false
      modelToDelete.value = null
      fetchModels()
    } else {
      ElMessage.error(response.error || '模型删除失败')
    }
  } catch (error) {
    // 检查是否是权限错误
    if (error.response?.status === 403) {
      ElMessage.error('权限不足：需要管理员权限')
    } else if (error.response?.status === 401) {
      ElMessage.error('请先登录')
    } else {
      ElMessage.error('模型删除失败')
    }
  } finally {
    deleting.value = false
  }
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

.upload-form {
  margin-bottom: 16px;
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

.upload-progress {
  margin-top: 16px;
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