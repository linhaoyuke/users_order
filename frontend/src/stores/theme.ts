import {defineStore} from 'pinia'
import {ref} from 'vue'

export type ThemeType = 'default' | 'green' | 'pink'

export interface Theme {
  name: string
  type: ThemeType
  colors: {
    primary: string
    primaryLight: string
    primaryDark: string
    success: string
    warning: string
    danger: string
    info: string
  }
}

export const themes: Record<ThemeType, Theme> = {
  default: {
    name: '默认主题',
    type: 'default',
    colors: {
      primary: '#409eff',
      primaryLight: '#79bbff',
      primaryDark: '#337ecc',
      success: '#67c23a',
      warning: '#e6a23c',
      danger: '#f56c6c',
      info: '#909399'
    }
  },
  green: {
    name: '绿色主题',
    type: 'green',
    colors: {
      primary: '#67c23a',
      primaryLight: '#95d475',
      primaryDark: '#529b2e',
      success: '#67c23a',
      warning: '#e6a23c',
      danger: '#f56c6c',
      info: '#909399'
    }
  },
  pink: {
    name: '粉色主题',
    type: 'pink',
    colors: {
      primary: '#f56c6c',
      primaryLight: '#fbc4c4',
      primaryDark: '#c45656',
      success: '#67c23a',
      warning: '#e6a23c',
      danger: '#f56c6c',
      info: '#909399'
    }
  }
}

export const useThemeStore = defineStore('theme', () => {
  // 安全地从localStorage初始化主题
  const getInitialTheme = (): ThemeType => {
    if (typeof window === 'undefined') return 'default'
    try {
      const saved = localStorage.getItem('theme') as ThemeType
      return (saved && themes[saved]) ? saved : 'default'
    } catch {
      return 'default'
    }
  }
  
  const currentTheme = ref<ThemeType>(getInitialTheme())

  // 应用主题
  const applyTheme = (theme: ThemeType) => {
    const themeConfig = themes[theme]
    const root = document.documentElement
    const body = document.body

    // 移除之前的主题类
    body.classList.remove('green-theme', 'default-theme', 'pink-theme')
    
    // 添加新的主题类
    body.classList.add(`${theme}-theme`)
    
    // 设置data属性用于CSS选择器
    root.setAttribute('data-theme', theme)

    // 设置CSS变量
    Object.entries(themeConfig.colors).forEach(([key, value]) => {
      const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase()
      root.style.setProperty(`--el-color-${cssKey}`, value)
    })

    // 特殊处理primary相关的衍生颜色
    root.style.setProperty('--el-color-primary', themeConfig.colors.primary)
    root.style.setProperty('--el-color-primary-light-3', themeConfig.colors.primaryLight)
    root.style.setProperty('--el-color-primary-light-5', themeConfig.colors.primaryLight)
    root.style.setProperty('--el-color-primary-light-7', themeConfig.colors.primaryLight)
    root.style.setProperty('--el-color-primary-light-8', themeConfig.colors.primaryLight)
    root.style.setProperty('--el-color-primary-light-9', themeConfig.colors.primaryLight)
    root.style.setProperty('--el-color-primary-dark-2', themeConfig.colors.primaryDark)

    // 添加切换动画
    body.classList.add('theme-switching')
    setTimeout(() => {
      body.classList.remove('theme-switching')
    }, 600)

    // 更新当前主题
    currentTheme.value = theme
    
    // 安全地保存到localStorage
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('theme', theme)
      } catch (error) {
        console.warn('保存主题设置失败:', error)
      }
    }
  }

  // 切换主题
  const switchTheme = (theme: ThemeType) => {
    applyTheme(theme)
  }

  // 获取当前主题配置
  const getCurrentTheme = () => {
    return themes[currentTheme.value]
  }

  // 初始化时应用主题
  applyTheme(currentTheme.value)

  return {
    currentTheme,
    switchTheme,
    getCurrentTheme,
    themes
  }
})