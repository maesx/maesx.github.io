# 图像分割可视化平台 - 前端

## 技术栈

- **Vue.js 3**: 渐进式前端框架
- **Element Plus**: UI组件库
- **Vue Router**: 路由管理
- **Axios**: HTTP请求
- **ECharts**: 数据可视化
- **Vite**: 构建工具

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API接口
│   │   ├── index.js    # API配置
│   │   └── modules.js  # API模块
│   ├── assets/         # 资源文件
│   ├── components/     # 公共组件
│   ├── router/         # 路由配置
│   ├── utils/          # 工具函数
│   ├── views/          # 页面组件
│   │   ├── Login.vue      # 登录页
│   │   ├── Layout.vue     # 布局页
│   │   ├── Segment.vue    # 图像分割页
│   │   ├── History.vue    # 历史记录页
│   │   ├── Compare.vue    # 结果对比页
│   │   ├── Models.vue     # 模型管理页
│   │   └── Augmentation.vue # 数据增强页
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html          # HTML模板
├── vite.config.js      # Vite配置
└── package.json        # 项目配置
```

## 功能特性

### 1. 登录功能
- 保留登录界面（无验证，直接放行）

### 2. 图像分割
- 支持单张/批量图片上传
- 支持语义分割和实例分割
- 实时展示分割结果
- IoU、准确率等指标展示
- 图表可视化（IoU分布、像素分布）

### 3. 历史记录
- 查看分割历史
- 支持删除记录
- 快速添加到对比列表

### 4. 结果对比
- 选择多个结果进行对比
- 并排展示分割效果
- 差异分析表格

### 5. 模型管理
- 查看所有可用模型
- 上传自定义模型
- 查看模型性能指标

### 6. 数据增强
- 数据增强参数说明
- 简洁易懂的文案
- 适合非专业人士阅读

### 7. GPU监控
- 侧边栏实时显示GPU状态
- 支持CUDA和MPS设备

## API接口

所有API通过 `/api` 前缀访问，后端服务运行在 `http://127.0.0.1:5000`

### 主要接口

- `POST /api/login` - 用户登录
- `GET /api/models` - 获取模型列表
- `POST /api/models/upload` - 上传模型
- `POST /api/segment` - 单张图像分割
- `POST /api/segment/batch` - 批量图像分割
- `GET /api/segment/history` - 获取历史记录
- `GET /api/gpu/status` - 获取GPU状态
- `GET /api/augmentation/preview` - 获取数据增强说明

## 开发注意事项

1. 所有API请求使用axios拦截器统一处理
2. Element Plus图标全局注册
3. 路由支持懒加载
4. 支持热重载开发
5. 生产构建优化
