/**
 * Vue Router 配置
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/segment',
    children: [
      {
        path: 'segment',
        name: 'Segment',
        component: () => import('@/views/Segment.vue'),
        meta: { title: '图像分割' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '历史记录' }
      },
      {
        path: 'compare',
        name: 'Compare',
        component: () => import('@/views/Compare.vue'),
        meta: { title: '结果对比' }
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/Models.vue'),
        meta: { title: '模型管理' }
      },
      {
        path: 'augmentation',
        name: 'Augmentation',
        component: () => import('@/views/Augmentation.vue'),
        meta: { title: '数据增强' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 图像分割平台` : '图像分割可视化平台'
  next()
})

export default router
