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
    return api.delete('/segment/compare/clear')
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
  }
}
