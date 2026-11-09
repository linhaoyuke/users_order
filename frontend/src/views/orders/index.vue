<template>
  <TablePage
    title="订单管理"
    :data="orders"
    :loading="loading"
    :total="total"
    @add="handleAdd"
    @search="handleSearch"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <el-table-column prop="id" label="ID" min-width="120" show-overflow-tooltip />
    <el-table-column prop="order_number" label="订单号" min-width="180" show-overflow-tooltip />
    <el-table-column prop="user_id" label="用户ID" min-width="135" align="center">
      <template #default="{ row }">
        <el-tooltip :content="row.user_id ? `点击复制完整用户ID: ${row.user_id}` : '无用户ID'" placement="top" :show-after="200">
          <span class="uuid-pill" @click="copyText(row.user_id)">
            <span class="uuid-text">{{ formatUuid(row.user_id) }}</span>
            <el-icon class="copy-icon"><CopyDocument /></el-icon>
          </span>
        </el-tooltip>
      </template>
    </el-table-column>
    <el-table-column label="用户名" min-width="150" show-overflow-tooltip>
      <template #default="{ row }">
        <div class="user-cell">
          <span class="username">{{ row.user_username || '未知用户' }}</span>
          <span class="full-name" v-if="row.user_full_name">({{ row.user_full_name }})</span>
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="total_amount" label="总金额" width="120" align="right">
      <template #default="{ row }">
        <span class="amount-text">¥{{ Number(row.total_amount).toFixed(2) }}</span>
      </template>
    </el-table-column>
    <el-table-column label="订单状态" width="110" align="center">
      <template #default="{ row }">
        <el-tag :type="getOrderStatusType(row.status)">
          {{ (ORDER_STATUS_LABELS as any)[row.status] || row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="支付状态" width="110" align="center">
      <template #default="{ row }">
        <el-tag :type="getPaymentStatusType(row.payment_status)">
          {{ (PAYMENT_STATUS_LABELS as any)[row.payment_status] || row.payment_status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="shipping_address" label="收货地址" min-width="200" show-overflow-tooltip />
    <el-table-column prop="created_at" label="创建时间" width="170" align="center">
      <template #default="{ row }">
        {{ formatDate(row.created_at) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="260" fixed="right" align="center">
      <template #default="{ row }">
        <div class="action-buttons">
          <el-button type="info" size="small" @click="handleView(row)">
            查看
          </el-button>
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="warning" size="small" @click="handleUpdateStatus(row)">
            状态
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </div>
      </template>
    </el-table-column>
  </TablePage>

  <!-- 订单表单对话框 -->
  <OrderForm
    v-model="showOrderForm"
    :order="currentOrder"
    @success="handleFormSuccess"
  />

  <!-- 订单详情对话框 -->
  <OrderDetailDialog
    v-model="showDetailDialog"
    :order="currentOrder"
  />

  <!-- 状态更新对话框 -->
  <OrderStatusDialog
    v-model="showStatusDialog"
    :order="currentOrder"
    @success="handleStatusUpdateSuccess"
  />
</template>

<script setup lang="ts">
import {onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import TablePage from '@/components/TablePage.vue'
import OrderForm from './components/OrderForm.vue'
import OrderDetailDialog from './components/OrderDetailDialog.vue'
import OrderStatusDialog from './components/OrderStatusDialog.vue'
import {orderApi} from '@/api/order'
import type {Order} from '@/types/order'
import {ORDER_STATUS_LABELS, PAYMENT_STATUS_LABELS} from '@/types/order'
import {formatDate} from '@/utils/date'
import {CopyDocument} from '@element-plus/icons-vue'

// 格式化展示 UUID（截取前8位 + ...，悬停可查看完整ID）
const formatUuid = (uuid?: string) => {
  if (!uuid) return '-'
  if (uuid.length <= 10) return uuid
  return `${uuid.slice(0, 8)}...`
}

// 复制文本到剪贴板
const copyText = (text?: string) => {
  if (!text) return
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success('已复制用户ID到剪贴板')
    }).catch(() => {
      fallbackCopy(text)
    })
  } else {
    fallbackCopy(text)
  }
}

const fallbackCopy = (text: string) => {
  const textArea = document.createElement('textarea')
  textArea.value = text
  textArea.style.position = 'fixed'
  textArea.style.opacity = '0'
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()
  try {
    document.execCommand('copy')
    ElMessage.success('已复制用户ID到剪贴板')
  } catch (err) {
    ElMessage.warning('复制失败，请手动选择复制')
  }
  document.body.removeChild(textArea)
}

const orders = ref<Order[]>([])
const loading = ref(false)
const showOrderForm = ref(false)
const showDetailDialog = ref(false)
const showStatusDialog = ref(false)
const currentOrder = ref<Order | null>(null)

// 分页和搜索相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

// 获取订单状态标签类型
const getOrderStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending_payment: 'warning',
    paid: 'success',
    shipped: 'info',
    delivered: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

// 获取支付状态标签类型
const getPaymentStatusType = (status: string) => {
  const types: Record<string, string> = {
    unpaid: 'warning',
    paid: 'success',
    refunded: 'info'
  }
  return types[status] || 'info'
}

// 获取订单列表
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchKeyword.value
    }
    const response = await orderApi.getOrders(params)
    orders.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 新增订单
const handleAdd = () => {
  currentOrder.value = null
  showOrderForm.value = true
}

// 查看订单
const handleView = async (order: Order) => {
  loading.value = true
  try {
    const response = await orderApi.getOrder(order.id)
    currentOrder.value = response.data
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('获取订单详情失败')
  } finally {
    loading.value = false
  }
}

// 编辑订单
const handleEdit = async (order: Order) => {
  loading.value = true
  try {
    // 先获取完整的订单详情（包括订单项）
    const response = await orderApi.getOrder(order.id)
    currentOrder.value = response.data
    showOrderForm.value = true
  } catch (error) {
    ElMessage.error('获取订单详情失败')
  } finally {
    loading.value = false
  }
}

// 更新状态
const handleUpdateStatus = (order: Order) => {
  currentOrder.value = order
  showStatusDialog.value = true
}

// 删除订单
const handleDelete = async (order: Order) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除订单 "${order.order_number}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await orderApi.deleteOrder(order.id)
    ElMessage.success('删除成功')
    fetchOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 搜索
const handleSearch = (keyword: string) => {
  searchKeyword.value = keyword
  currentPage.value = 1 // 搜索时重置到第一页
  fetchOrders()
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 改变页面大小时重置到第一页
  fetchOrders()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchOrders()
}

// 表单提交成功
const handleFormSuccess = async () => {
  // 刷新订单列表
  await fetchOrders()
  
  // 如果是编辑模式且有当前订单，重新获取该订单的最新数据
  if (currentOrder.value && currentOrder.value.id) {
    try {
      const response = await orderApi.getOrder(currentOrder.value.id)
      currentOrder.value = response.data
    } catch (error) {
      // 如果获取失败，清空当前订单
      currentOrder.value = null
    }
  }
}

// 状态更新成功
const handleStatusUpdateSuccess = () => {
  fetchOrders()
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.uuid-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
  font-size: 12px;
  color: #606266;
  background-color: #f4f4f5;
  border: 1px solid #e4e7ed;
  padding: 2px 7px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  line-height: 1.4;
}

.uuid-pill:hover {
  color: #409eff;
  background-color: #ecf5ff;
  border-color: #c6e2ff;
}

.copy-icon {
  font-size: 11px;
  opacity: 0.6;
}

.uuid-pill:hover .copy-icon {
  opacity: 1;
}

.user-cell {
  display: flex;
  align-items: baseline;
  gap: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.username {
  font-weight: 500;
  color: #409eff;
}

.full-name {
  font-size: 12px;
  color: #909399;
}

.amount-text {
  font-weight: 600;
  color: #f56c6c;
  font-family: 'Consolas', 'Menlo', monospace;
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
  padding: 5px 8px;
}

/* 响应式处理 */
@media (max-width: 1200px) {
  .action-buttons {
    flex-direction: column;
    gap: 4px;
    align-items: stretch;
  }

  .action-buttons .el-button {
    width: 100%;
    min-width: auto;
  }
}
</style>
