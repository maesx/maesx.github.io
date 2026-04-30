/**
 * 模型管理API
 */
import api from './index'

export const modelApi = {
  /**
   * 获取模型列表
   */
  getModels() {
    return api.get('/models')
  },

  /**
   * 获取模型详情
   */
  getModelDetail(modelName) {
    return api.get(`/models/${modelName}`)
  },

  /**
   * 上传模型
   */
  uploadModel(formData, onProgress) {
    return api.post('/models/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  /**
   * 删除模型
   */
  deleteModel(modelName) {
    return api.delete(`/models/${modelName}`)
  }
}

/**
 * 图像分割API
 */
export const segmentApi = {
  /**
   * 单张图像分割
   */
  segment(formData, onProgress) {
    return api.post('/segment', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  /**
   * 批量图像分割
   */
  batchSegment(formData, onProgress) {
    return api.post('/segment/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  /**
   * 获取历史记录
   */
  getHistory() {
    return api.get('/segment/history')
  },

  /**
   * 删除历史记录
   */
  deleteHistory(recordId) {
    return api.delete(`/segment/history/${recordId}`)
  },

  /**
   * 获取对比列表
   */
  getCompareList() {
    return api.get('/segment/compare/list')
  },

  /**
   * 从对比列表中移除
   */
  removeFromCompare(id) {
    return api.delete(`/segment/compare/${id}`)
  },

  /**
   * 清空对比列表
   */
  clearCompare() {
    return api.post('/segment/compare/clear')  // 后端使用POST方法
  },

  /**
   * 添加到对比列表
   */
  addToCompare(resultId) {
    return api.post(`/segment/compare/add/${resultId}`)
  }
}

/**
 * 可视化API
 */
export const visualizationApi = {
  /**
   * 获取可视化数据
   */
  getVisualization(resultId) {
    return api.get(`/visualization/${resultId}`)
  },

  /**
   * 获取GPU状态
   */
  getGPUStatus() {
    return api.get('/gpu/status')
  }
}

/**
 * 数据增强API
 */
export const augmentationApi = {
  /**
   * 获取数据增强参数
   */
  getAugmentations() {
    return api.get('/augmentation/preview')
  },

  /**
   * 生成预览
   */
  preview(formData, onProgress) {
    return api.post('/augmentation/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  /**
   * 下载ZIP
   */
  downloadZip(results) {
    const formData = new FormData()
    formData.append('results', JSON.stringify(results))
    
    return api.post('/augmentation/download', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
  }
}

/**
 * 认证API
 */
export const authApi = {
  /**
   * 登录
   */
  login(credentials) {
    return api.post('/login', credentials)
  },

  /**
   * 注册
   */
  register(userData) {
    return api.post('/register', userData)
  }
}

/**
 * 个人中心API
 */
export const profileApi = {
  /**
   * 获取用户资料
   */
  getProfile(userId) {
    return api.get(`/profile/${userId}`)
  },

  /**
   * 更新用户资料
   */
  updateProfile(userId, data) {
    return api.put(`/profile/${userId}`, data)
  },

  /**
   * 上传头像
   */
  uploadAvatar(userId, data) {
    return api.post(`/profile/${userId}/avatar`, data)
  },

  /**
   * 删除头像
   */
  deleteAvatar(userId) {
    return api.delete(`/profile/${userId}/avatar`)
  },

  /**
   * 修改密码
   */
  changePassword(userId, data) {
    return api.put(`/profile/${userId}/password`, data)
  }
}

/**
 * 系统设置API
 */
export const settingsApi = {
  /**
   * 获取系统配置
   */
  getConfig() {
    return api.get('/settings/config')
  },

  /**
   * 更新系统配置
   */
  updateConfig(config) {
    return api.put('/settings/config', config)
  },

  /**
   * 获取存储信息
   */
  getStorageInfo() {
    return api.get('/settings/storage')
  },

  /**
   * 获取系统日志
   */
  getLogs(params) {
    return api.get('/settings/logs', { params })
  }
}
