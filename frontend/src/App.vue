<template>
  <router-view />
</template>

<style>
:root {
  /* 生态绿色系主题 - 更加现代化和专业 */
  --primary-green: #2d8a4e;      /* 主题绿：代表森林与生态 */
  --secondary-green: #1b5e20;    /* 深绿：用于强调和悬停 */
  --accent-green: #4caf50;       /* 亮绿：用于辅助和点缀 */
  --light-green: #f1f8e9;        /* 极浅绿：用于背景块 */
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --danger-color: #f56c6c;
  --info-color: #909399;

  /* 文字颜色 */
  --text-primary: #000000;       /* 标题颜色：纯黑，满足用户要求 */
  --text-regular: #303133;       /* 正文颜色 */
  --text-secondary: #606266;     /* 次要文字 */
  --text-placeholder: #a8abb2;   /* 占位文字 */
  --text-dark: var(--text-primary);    /* 兼容旧代码 */
  --text-gray: var(--text-secondary);  /* 兼容旧代码 */

  /* 背景与边框 */
  --bg-light: #f8fafc;           /* 更柔和的非纯白背景 */
  --main-bg-soft: #f1f5f9;
  --border-color: #e2e8f0;
  --header-bg: linear-gradient(to right, #ffffff, #f8fafc);
  
  /* 阴影与圆角 */
  --shadow-subtle: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
  --radius-main: 12px;
  --radius-sm: 6px;
  --transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-light);
  color: var(--text-regular);
}

/* 标题样式统一优化 */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary); /* 将所有标题设为黑色 */
  margin-top: 0;
  font-weight: 600;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

#app {
  width: 100%;
  height: 100vh;
}

/* 全局滚动条优化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* Element Plus 样式覆盖 */
.el-card {
  border-radius: var(--radius-main) !important;
  border: none !important;
  box-shadow: var(--shadow-subtle) !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.el-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1) !important;
}

.el-button--primary {
  background-color: var(--primary-green) !important;
  border-color: var(--primary-green) !important;
}

.el-button--primary:hover {
  background-color: var(--accent-green) !important;
  border-color: var(--accent-green) !important;
  opacity: 0.9;
}

/* 页面切换动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.5s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
