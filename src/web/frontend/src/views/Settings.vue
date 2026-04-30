<template>
  <div class="settings-container">
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 通用设置 -->
      <el-tab-pane label="通用设置" name="general">
        <el-card>
          <el-form 
            :model="configForm.general" 
            label-width="180px"
            v-loading="configLoading"
          >
            <el-divider content-position="left">基本设置</el-divider>
            
            <el-form-item label="应用名称">
              <el-input v-model="configForm.general.app_name" />
            </el-form-item>
            
            <el-form-item label="默认语言">
              <el-select v-model="configForm.general.default_language" style="width: 200px">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            
            <el-divider content-position="left">上传设置</el-divider>
            
            <el-form-item label="最大上传大小">
              <el-input-number 
                v-model="configForm.general.upload_max_size" 
                :min="1" 
                :max="100"
              />
              <span class="form-tip">MB</span>
            </el-form-item>
            
            <el-divider content-position="left">系统设置</el-divider>
            
            <el-form-item label="会话超时时间">
              <el-input-number 
                v-model="configForm.general.session_timeout" 
                :min="600"
                :max="86400"
                :step="60"
              />
              <span class="form-tip">秒</span>
            </el-form-item>
            
            <el-form-item label="启用GPU加速">
              <el-switch v-model="configForm.general.enable_gpu" />
            </el-form-item>
            
            <el-form-item label="自动保存结果">
              <el-switch v-model="configForm.general.auto_save" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleSaveConfig" :loading="saveLoading">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 存储设置 -->
      <el-tab-pane label="存储管理" name="storage">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>磁盘空间</span>
                  <el-button type="primary" size="small" @click="loadStorageInfo">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              
              <div class="disk-info" v-if="storageInfo.disk">
                <el-progress 
                  :percentage="storageInfo.disk.used_percent" 
                  :color="getProgressColor(storageInfo.disk.used_percent)"
                />
                <div class="disk-details">
                  <p><strong>总空间:</strong> {{ storageInfo.disk.total_gb }} GB</p>
                  <p><strong>已使用:</strong> {{ storageInfo.disk.used_gb }} GB</p>
                  <p><strong>可用空间:</strong> {{ storageInfo.disk.free_gb }} GB</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="storage-card" style="margin-top: 20px">
          <template #header>
            <span>目录使用情况</span>
          </template>
          
          <el-table :data="directoryData" style="width: 100%">
            <el-table-column prop="name" label="目录名称" width="150" />
            <el-table-column prop="path" label="路径" />
            <el-table-column prop="size_mb" label="大小 (MB)" width="120">
              <template #default="{ row }">
                {{ row.size_mb.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="files" label="文件数" width="100" />
          </el-table>
        </el-card>
        
        <el-card class="storage-card" style="margin-top: 20px">
          <el-form 
            :model="configForm.storage" 
            label-width="180px"
          >
            <el-divider content-position="left">存储设置</el-divider>
            
            <el-form-item label="最大存储空间">
              <el-input-number 
                v-model="configForm.storage.max_storage_gb" 
                :min="10"
                :max="1000"
              />
              <span class="form-tip">GB</span>
            </el-form-item>
            
            <el-form-item label="自动清理">
              <el-switch v-model="configForm.storage.auto_cleanup" />
            </el-form-item>
            
            <el-form-item label="保留天数">
              <el-input-number 
                v-model="configForm.storage.retention_days" 
                :min="1"
                :max="365"
              />
              <span class="form-tip">天</span>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleSaveConfig" :loading="saveLoading">
                保存设置
              </el-button>
              <el-button type="danger" @click="handleCleanupStorage">
                清理过期文件
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 模型设置 -->
      <el-tab-pane label="模型配置" name="model">
        <el-card>
          <el-form 
            :model="configForm.model" 
            label-width="180px"
          >
            <el-divider content-position="left">默认模型配置</el-divider>
            
            <el-form-item label="默认模型">
              <el-input v-model="configForm.model.default_model" />
            </el-form-item>
            
            <el-form-item label="默认编码器">
              <el-select v-model="configForm.model.default_encoder" style="width: 200px">
                <el-option label="VGG19" value="vgg19" />
                <el-option label="VGG16" value="vgg16" />
                <el-option label="ResNet50" value="resnet50" />
                <el-option label="ResNet34" value="resnet34" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="默认类别数">
              <el-input-number 
                v-model="configForm.model.default_num_classes" 
                :min="2"
                :max="100"
              />
            </el-form-item>
            
            <el-divider content-position="left">训练参数</el-divider>
            
            <el-form-item label="批次大小">
              <el-input-number 
                v-model="configForm.model.batch_size" 
                :min="1"
                :max="32"
              />
            </el-form-item>
            
            <el-form-item label="图像尺寸">
              <el-input-number 
                v-model="configForm.model.image_size[0]" 
                :min="128"
                :max="1024"
                :step="64"
              />
              <span class="form-tip">×</span>
              <el-input-number 
                v-model="configForm.model.image_size[1]" 
                :min="128"
                :max="1024"
                :step="64"
              />
            </el-form-item>
            
            <el-form-item label="启用深度监督">
              <el-switch v-model="configForm.model.use_deep_supervision" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleSaveConfig" :loading="saveLoading">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 系统日志 -->
      <el-tab-pane label="系统日志" name="logs">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>日志列表</span>
              <div>
                <el-select 
                  v-model="logLevel" 
                  placeholder="日志级别" 
                  style="width: 120px; margin-right: 10px"
                  @change="handleLogLevelChange"
                >
                  <el-option label="全部" value="" />
                  <el-option label="INFO" value="INFO" />
                  <el-option label="WARNING" value="WARNING" />
                  <el-option label="ERROR" value="ERROR" />
                </el-select>
                <el-button type="primary" size="small" @click="loadLogs">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="logs" 
            style="width: 100%"
            max-height="600"
            v-loading="logsLoading"
          >
            <el-table-column prop="timestamp" label="时间" width="180" />
            <el-table-column prop="level" label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="getLogLevelType(row.level)" size="small">
                  {{ row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="file" label="文件" width="150" />
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { settingsApi } from '@/api/modules'

const activeTab = ref('general')
const configLoading = ref(false)
const saveLoading = ref(false)
const logsLoading = ref(false)
const logLevel = ref('')

const configForm = reactive({
  general: {
    app_name: '图像分割可视化平台',
    default_language: 'zh-CN',
    upload_max_size: 50,
    session_timeout: 3600,
    enable_gpu: true,
    auto_save: true
  },
  storage: {
    upload_dir: 'uploads',
    result_dir: 'results',
    model_dir: 'checkpoints',
    max_storage_gb: 100,
    auto_cleanup: true,
    retention_days: 30
  },
  model: {
    default_model: 'best_model.pth',
    default_encoder: 'vgg19',
    default_num_classes: 4,
    batch_size: 4,
    image_size: [512, 512],
    use_deep_supervision: true
  }
})

const storageInfo = reactive({
  disk: null,
  directories: {}
})

const logs = ref([])

const directoryData = computed(() => {
  const data = []
  for (const [name, info] of Object.entries(storageInfo.directories)) {
    data.push({
      name: getDirectoryName(name),
      path: info.path,
      size_mb: info.size_mb || 0,
      files: info.files || 0
    })
  }
  return data
})

const getDirectoryName = (name) => {
  const names = {
    uploads: '上传文件',
    results: '分割结果',
    models: '模型文件',
    logs: '日志文件'
  }
  return names[name] || name
}

const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getLogLevelType = (level) => {
  const types = {
    INFO: 'info',
    WARNING: 'warning',
    ERROR: 'danger',
    DEBUG: ''
  }
  return types[level] || ''
}

// 加载系统配置
const loadConfig = async () => {
  try {
    configLoading.value = true
    
    // TODO: 调用API获取配置
    // const response = await settingsApi.getConfig()
    // if (response.success) {
    //   Object.assign(configForm, response.config)
    // }
    
    configLoading.value = false
  } catch (error) {
    configLoading.value = false
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 保存系统配置
const handleSaveConfig = async () => {
  try {
    saveLoading.value = true
    
    // TODO: 调用API保存配置
    // const response = await settingsApi.updateConfig(configForm)
    // if (response.success) {
    //   ElMessage.success('配置保存成功')
    // }
    
    ElMessage.success('配置保存成功')
    saveLoading.value = false
  } catch (error) {
    saveLoading.value = false
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 加载存储信息
const loadStorageInfo = async () => {
  try {
    // TODO: 调用API获取存储信息
    // const response = await settingsApi.getStorageInfo()
    // if (response.success) {
    //   storageInfo.disk = response.storage.disk
    //   storageInfo.directories = response.storage.directories
    // }
    
    // 模拟数据
    storageInfo.disk = {
      total_gb: 256.0,
      used_gb: 128.5,
      free_gb: 127.5,
      used_percent: 50.2
    }
    storageInfo.directories = {
      uploads: { path: 'uploads', size_mb: 512.3, files: 128 },
      results: { path: 'outputs/results', size_mb: 1024.6, files: 256 },
      models: { path: 'outputs/checkpoints', size_mb: 2048.9, files: 15 },
      logs: { path: 'logs', size_mb: 64.2, files: 8 }
    }
  } catch (error) {
    console.error('加载存储信息失败:', error)
    ElMessage.error('加载存储信息失败')
  }
}

// 加载日志
const loadLogs = async () => {
  try {
    logsLoading.value = true
    
    // TODO: 调用API获取日志
    // const response = await settingsApi.getLogs({ limit: 100, level: logLevel.value })
    // if (response.success) {
    //   logs.value = response.logs
    // }
    
    // 模拟数据
    logs.value = [
      {
        timestamp: '2026-04-27 13:45:32',
        level: 'INFO',
        file: 'app.log',
        content: '[INFO] 应用启动成功，监听端口 5000'
      },
      {
        timestamp: '2026-04-27 13:46:15',
        level: 'INFO',
        file: 'app.log',
        content: '[INFO] 模型加载成功: best_model.pth'
      },
      {
        timestamp: '2026-04-27 13:47:22',
        level: 'WARNING',
        file: 'app.log',
        content: '[WARNING] GPU内存不足，使用CPU模式'
      },
      {
        timestamp: '2026-04-27 13:48:45',
        level: 'ERROR',
        file: 'app.log',
        content: '[ERROR] 文件上传失败: 文件大小超过限制'
      }
    ]
    
    logsLoading.value = false
  } catch (error) {
    logsLoading.value = false
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  }
}

// 日志级别变更
const handleLogLevelChange = () => {
  loadLogs()
}

// 清理存储
const handleCleanupStorage = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清理过期文件吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API清理存储
    // const response = await settingsApi.cleanupStorage()
    // if (response.success) {
    //   ElMessage.success(`已清理 ${response.deleted_files} 个文件，释放 ${response.freed_mb} MB 空间`)
    //   loadStorageInfo()
    // }
    
    ElMessage.success('清理完成')
    loadStorageInfo()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清理存储失败:', error)
      ElMessage.error('清理存储失败')
    }
  }
}

onMounted(() => {
  loadConfig()
  loadStorageInfo()
  loadLogs()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.settings-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
}

.disk-info {
  padding: 20px 0;
}

.disk-details {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.disk-details p {
  margin: 0;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.storage-card {
  margin-top: 20px;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #303133;
}
</style>
