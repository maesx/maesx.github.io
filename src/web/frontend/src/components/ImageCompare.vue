<template>
  <div class="image-compare-container" ref="containerRef">
    <!-- 原图层（底层，始终可见） -->
    <div class="image-layer original-layer">
      <img :src="originalImage" alt="原图" @load="onImageLoad" />
    </div>
    
    <!-- 分割结果层（顶层，半透明融合） -->
    <div 
      class="image-layer result-layer" 
      :style="{ opacity: sliderPosition / 100 }"
    >
      <img :src="resultImage" alt="分割结果" />
    </div>
    
    <!-- 滑块 -->
    <div 
      class="slider-handle"
      :style="{ left: sliderPosition + '%' }"
      @mousedown="startDrag"
      @touchstart.passive="startDrag"
    >
      <div class="slider-line"></div>
      <div class="slider-button">
        <el-icon><DArrowLeft /></el-icon>
        <el-icon><DArrowRight /></el-icon>
      </div>
    </div>
    
    <!-- 标签（动态显示） -->
    <div class="label result-label" v-show="sliderPosition > 15">
      分割结果 ({{ Math.round(sliderPosition) }}%)
    </div>
    <div class="label original-label" v-show="sliderPosition < 85">
      原图 ({{ 100 - Math.round(sliderPosition) }}%)
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { DArrowLeft, DArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  originalImage: {
    type: String,
    required: true
  },
  resultImage: {
    type: String,
    required: true
  }
})

const containerRef = ref(null)
const sliderPosition = ref(50) // 滑块位置，百分比
const isDragging = ref(false)

const onImageLoad = () => {
  // 图片加载完成
}

const startDrag = (e) => {
  e.preventDefault()
  isDragging.value = true
  
  // 添加全局事件监听
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

const onDrag = (e) => {
  if (!isDragging.value || !containerRef.value) return
  
  const rect = containerRef.value.getBoundingClientRect()
  let clientX
  
  // 支持触摸事件
  if (e.type === 'touchmove') {
    e.preventDefault()
    clientX = e.touches[0].clientX
  } else {
    clientX = e.clientX
  }
  
  // 计算滑块位置
  const position = ((clientX - rect.left) / rect.width) * 100
  
  // 限制范围 [0, 100]，允许完全重叠
  sliderPosition.value = Math.max(0, Math.min(100, position))
}

const stopDrag = () => {
  isDragging.value = false
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
}

onBeforeUnmount(() => {
  // 组件卸载时清理事件监听
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
})
</script>

<style scoped>
.image-compare-container {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
  background: #f5f5f5;
  user-select: none;
}

.image-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.image-layer img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  pointer-events: none;
}

.result-layer {
  z-index: 2;
}

.slider-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 40px;
  margin-left: -20px;
  cursor: ew-resize;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slider-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  background: #1890ff;
  transform: translateX(-50%);
}

.slider-button {
  position: relative;
  z-index: 11;
  background: #1890ff;
  color: white;
  padding: 8px 4px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s;
}

.slider-button:hover {
  transform: scale(1.1);
}

.slider-button .el-icon {
  font-size: 12px;
}

.label {
  position: absolute;
  bottom: 16px;
  padding: 6px 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  z-index: 5;
  pointer-events: none;
}

.original-label {
  left: 16px;
}

.result-label {
  right: 16px;
}
</style>
