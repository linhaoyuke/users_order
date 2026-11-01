<template>
  <div class="theme-switcher">
    <h5 style="margin-bottom: 16px; color: #303133;">主题选择</h5>
    
    <div class="theme-preview-container">
      <div 
        v-for="(theme, key) in themes" 
        :key="key"
        class="theme-preview"
        :class="{ active: currentTheme === key }"
        @click="handleThemeChange(key)"
      >
        <div class="theme-colors">
          <div 
            class="color-block primary" 
            :style="{ backgroundColor: theme.colors.primary }"
            :title="'主色调: ' + theme.colors.primary"
          ></div>
          <div 
            class="color-block success" 
            :style="{ backgroundColor: theme.colors.success }"
            :title="'成功色: ' + theme.colors.success"
          ></div>
          <div 
            class="color-block warning" 
            :style="{ backgroundColor: theme.colors.warning }"
            :title="'警告色: ' + theme.colors.warning"
          ></div>
          <div 
            class="color-block danger" 
            :style="{ backgroundColor: theme.colors.danger }"
            :title="'危险色: ' + theme.colors.danger"
          ></div>
        </div>
        <div class="theme-name">{{ theme.name }}</div>
        <div v-if="currentTheme === key" class="theme-check">
          <el-icon><Check /></el-icon>
        </div>
      </div>
    </div>
    
    <div class="theme-description">
      <el-alert
        title="主题说明"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <p>选择您喜欢的主题颜色，设置会自动保存到本地。</p>
          <p class="current-theme-info">当前主题：<strong>{{ themes[currentTheme].name }}</strong></p>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from 'pinia'
import {type ThemeType, useThemeStore} from '@/stores/theme'
import {ElMessage} from 'element-plus'
import {Check} from '@element-plus/icons-vue'

const themeStore = useThemeStore()
const { currentTheme, themes } = storeToRefs(themeStore)

const handleThemeChange = (theme: ThemeType) => {
  themeStore.switchTheme(theme)
  ElMessage.success(`已切换到${themes.value[theme].name}`)
}
</script>

<style scoped>
.theme-switcher {
  padding: 20px 0;
}

.theme-preview-container {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.theme-preview {
  position: relative;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  min-width: 160px;
}

.theme-preview:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.theme-preview.active {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
}

.theme-colors {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
}

.color-block {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-block:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.theme-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  text-align: center;
}

.theme-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  background: var(--el-color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}

.theme-description {
  margin-top: 24px;
}

.current-theme-info {
  margin-top: 8px;
  font-size: 13px;
}

.current-theme-info strong {
  color: var(--el-color-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-preview-container {
    justify-content: center;
  }
  
  .theme-preview {
    min-width: 140px;
  }
}
</style>