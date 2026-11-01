<template>
  <div class="dashboard">
    <div class="page-container">
      <h1>欢迎使用后台管理系统</h1>
      
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row" v-loading="stats.loading" justify="space-around">
        <el-col :xs="24" :sm="12" :md="4">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon user-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.userCount }}</div>
                <div class="stats-label">用户总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="4">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon order-icon">
                <el-icon><ShoppingCart /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.orderCount }}</div>
                <div class="stats-label">订单总数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="4">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon product-icon">
                <el-icon><Goods /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.productCount }}</div>
                <div class="stats-label">商品总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="4">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon role-icon">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.roleCount }}</div>
                <div class="stats-label">角色总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="4">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon permission-icon">
                <el-icon><Lock /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.permissionCount }}</div>
                <div class="stats-label">权限总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 快捷操作 -->
      <el-card class="quick-actions" header="快捷操作">
        <div class="actions-container">
          <el-button type="primary" size="large" class="action-btn" @click="$router.push('/users')">
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
          <el-button type="success" size="large" class="action-btn" @click="$router.push('/orders')">
            <el-icon><ShoppingCart /></el-icon>
            订单管理
          </el-button>
          <el-button type="warning" size="large" class="action-btn" @click="$router.push('/roles')">
            <el-icon><UserFilled /></el-icon>
            角色管理
          </el-button>
          <el-button type="info" size="large" class="action-btn" @click="$router.push('/permissions')">
            <el-icon><Lock /></el-icon>
            权限管理
          </el-button>
          <el-button color="#626aef" size="large" class="action-btn" @click="$router.push('/products')">
            <el-icon><Goods /></el-icon>
            商品管理
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, reactive} from 'vue'
import {ElMessage} from 'element-plus'
import {statsApi} from '@/api/stats'

const stats = reactive({
  userCount: 0,
  orderCount: 0,
  roleCount: 0,
  permissionCount: 0,
  productCount: 0,
  loading: false
})

// 获取统计数据
const fetchStats = async () => {
  try {
    stats.loading = true
    const response = await statsApi.getDashboardStats()
    const data = response.data

    stats.userCount = data.user_stats.total_users
    stats.orderCount = data.order_stats.total_orders
    stats.roleCount = data.role_stats.total_roles
    stats.permissionCount = data.permission_stats.total_permissions
    stats.productCount = data.product_stats.total_products
  } catch (error) {
    ElMessage.error('获取统计数据失败')

    // 失败时使用默认值
    stats.userCount = 0
    stats.orderCount = 0
    stats.roleCount = 0
    stats.permissionCount = 0
    stats.productCount = 0
  } finally {
    stats.loading = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  height: 100%;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.stats-content {
  display: flex;
  align-items: center;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.user-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.order-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.product-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.role-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.permission-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  margin-top: 20px;
}

.actions-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 24px;
}

.action-btn {
  width: 160px;
  height: 60px;
  margin-bottom: 0;
  font-size: 16px;
}

@media (max-width: 768px) {
  .stats-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-icon {
    margin-right: 0;
    margin-bottom: 12px;
  }
}
</style>
