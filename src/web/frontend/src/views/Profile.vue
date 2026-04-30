<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧：个人信息卡片 -->
      <el-col :span="8">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
            </div>
          </template>
          
          <div class="avatar-section">
            <el-avatar 
              :size="120" 
              :src="userInfo.avatar" 
              :icon="UserFilled"
            />
            <div class="avatar-actions">
              <el-upload
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :http-request="handleAvatarUpload"
              >
                <el-button type="primary" size="small">
                  <el-icon><Upload /></el-icon>
                  更换头像
                </el-button>
              </el-upload>
              <el-button 
                v-if="userInfo.avatar"
                type="danger" 
                size="small"
                @click="handleDeleteAvatar"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
          
          <div class="info-section">
            <div class="info-item">
              <label>用户名</label>
              <span>{{ userInfo.username }}</span>
            </div>
            <div class="info-item">
              <label>昵称</label>
              <span>{{ userInfo.nickname || '未设置' }}</span>
            </div>
            <div class="info-item">
              <label>邮箱</label>
              <span>{{ userInfo.email }}</span>
            </div>
            <div class="info-item">
              <label>角色</label>
              <el-tag :type="userInfo.role === 'admin' ? 'danger' : 'info'">
                {{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
            <div class="info-item">
              <label>状态</label>
              <el-tag :type="userInfo.status === 1 ? 'success' : 'danger'">
                {{ userInfo.status === 1 ? '正常' : '禁用' }}
              </el-tag>
            </div>
            <div class="info-item">
              <label>注册时间</label>
              <span>{{ formatDateTime(userInfo.created_at) }}</span>
            </div>
            <div class="info-item">
              <label>最后登录</label>
              <span>{{ formatDateTime(userInfo.last_login_at) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：编辑表单 -->
      <el-col :span="16">
        <el-card class="edit-card">
          <el-tabs v-model="activeTab">
            <!-- 基本信息 -->
            <el-tab-pane label="基本信息" name="basic">
              <el-form 
                ref="profileFormRef"
                :model="profileForm"
                :rules="profileRules"
                label-width="100px"
              >
                <el-form-item label="用户名">
                  <el-input v-model="userInfo.username" disabled />
                </el-form-item>
                
                <el-form-item label="昵称" prop="nickname">
                  <el-input 
                    v-model="profileForm.nickname" 
                    placeholder="请输入昵称"
                    maxlength="50"
                    show-word-limit
                  />
                </el-form-item>
                
                <el-form-item label="邮箱" prop="email">
                  <el-input 
                    v-model="profileForm.email" 
                    placeholder="请输入邮箱"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="handleUpdateProfile"
                    :loading="profileLoading"
                  >
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <!-- 修改密码 -->
            <el-tab-pane label="修改密码" name="password">
              <el-form 
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="120px"
              >
                <el-form-item label="当前密码" prop="old_password">
                  <el-input 
                    v-model="passwordForm.old_password" 
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="new_password">
                  <el-input 
                    v-model="passwordForm.new_password" 
                    type="password"
                    placeholder="请输入新密码（至少8位）"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="确认密码" prop="confirm_password">
                  <el-input 
                    v-model="passwordForm.confirm_password" 
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="handleChangePassword"
                    :loading="passwordLoading"
                  >
                    修改密码
                  </el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <!-- 统计信息 -->
            <el-tab-pane label="统计信息" name="stats">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-statistic title="分割任务数" :value="stats.segmentations">
                    <template #prefix>
                      <el-icon><Edit /></el-icon>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="8">
                  <el-statistic title="数据增强数" :value="stats.augmentations">
                    <template #prefix>
                      <el-icon><MagicStick /></el-icon>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="8">
                  <el-statistic title="操作记录数" :value="stats.operations">
                    <template #prefix>
                      <el-icon><Document /></el-icon>
                    </template>
                  </el-statistic>
                </el-col>
              </el-row>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  UserFilled, 
  Upload, 
  Delete, 
  Edit,
  MagicStick,
  Document
} from '@element-plus/icons-vue'
import { profileApi } from '@/api/modules'

const activeTab = ref('basic')
const userInfo = ref({
  id: 1,
  username: 'Demo User',
  nickname: 'Demo User',
  email: 'demo@example.com',
  avatar: '',
  role: 'admin',
  status: 1,
  created_at: null,
  last_login_at: null
})

const profileFormRef = ref(null)
const passwordFormRef = ref(null)

const profileLoading = ref(false)
const passwordLoading = ref(false)

const profileForm = reactive({
  nickname: '',
  email: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const stats = reactive({
  segmentations: 128,
  augmentations: 45,
  operations: 256
})

const profileRules = {
  nickname: [
    { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少8位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    // 从localStorage获取用户信息
    const user = localStorage.getItem('user')
    if (user) {
      const userData = JSON.parse(user)
      userInfo.value = { ...userInfo.value, ...userData }
      
      // 同步到表单
      profileForm.nickname = userInfo.value.nickname || ''
      profileForm.email = userInfo.value.email || ''
    }
    
    // TODO: 从后端获取完整用户信息
    // const response = await profileApi.getProfile(userInfo.value.id)
    // if (response.success) {
    //   userInfo.value = response.user
    // }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  }
}

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 上传头像
const handleAvatarUpload = async (options) => {
  try {
    const file = options.file
    const reader = new FileReader()
    
    reader.onload = async (e) => {
      const base64 = e.target.result
      
      // TODO: 调用API上传头像
      // const response = await profileApi.uploadAvatar(userInfo.value.id, { avatar: base64 })
      // if (response.success) {
      //   userInfo.value.avatar = base64
      //   ElMessage.success('头像上传成功')
      // }
      
      // 临时更新头像显示
      userInfo.value.avatar = base64
      ElMessage.success('头像上传成功')
    }
    
    reader.readAsDataURL(file)
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('上传头像失败')
  }
}

// 删除头像
const handleDeleteAvatar = async () => {
  try {
    await ElMessageBox.confirm('确定要删除头像吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // TODO: 调用API删除头像
    // const response = await profileApi.deleteAvatar(userInfo.value.id)
    // if (response.success) {
    //   userInfo.value.avatar = ''
    //   ElMessage.success('头像删除成功')
    // }
    
    userInfo.value.avatar = ''
    ElMessage.success('头像删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除头像失败:', error)
      ElMessage.error('删除头像失败')
    }
  }
}

// 更新个人信息
const handleUpdateProfile = async () => {
  try {
    await profileFormRef.value.validate()
    
    profileLoading.value = true
    
    // TODO: 调用API更新个人信息
    // const response = await profileApi.updateProfile(userInfo.value.id, profileForm)
    // if (response.success) {
    //   userInfo.value.nickname = profileForm.nickname
    //   userInfo.value.email = profileForm.email
    //   localStorage.setItem('user', JSON.stringify(userInfo.value))
    //   ElMessage.success('资料更新成功')
    // }
    
    // 临时更新
    userInfo.value.nickname = profileForm.nickname
    userInfo.value.email = profileForm.email
    localStorage.setItem('user', JSON.stringify(userInfo.value))
    ElMessage.success('资料更新成功')
    
    profileLoading.value = false
  } catch (error) {
    profileLoading.value = false
    if (error !== 'cancel') {
      console.error('更新资料失败:', error)
      ElMessage.error('更新资料失败')
    }
  }
}

// 修改密码
const handleChangePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    
    passwordLoading.value = true
    
    // TODO: 调用API修改密码
    // const response = await profileApi.changePassword(userInfo.value.id, passwordForm)
    // if (response.success) {
    //   ElMessage.success('密码修改成功')
    //   resetPasswordForm()
    // }
    
    ElMessage.success('密码修改成功')
    resetPasswordForm()
    
    passwordLoading.value = false
  } catch (error) {
    passwordLoading.value = false
    if (error !== 'cancel') {
      console.error('修改密码失败:', error)
      ElMessage.error('修改密码失败')
    }
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields()
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

// 格式化日期时间
const formatDateTime = (datetime) => {
  if (!datetime) return '暂无数据'
  return new Date(datetime).toLocaleString('zh-CN')
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.avatar-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.info-section {
  margin-top: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  color: #606266;
  font-weight: 500;
}

.info-item span {
  color: #303133;
}

.edit-card {
  min-height: 500px;
}

:deep(.el-statistic__content) {
  font-size: 28px;
  margin-top: 10px;
}
</style>
