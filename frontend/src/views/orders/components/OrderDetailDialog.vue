<template>
  <el-dialog
    title="订单详情"
    :model-value="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    width="700px"
  >
    <div v-if="order" class="order-detail">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_number }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ new Date(order.created_at).toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ order.user_username }} ({{ order.user_full_name }})</el-descriptions-item>
        <el-descriptions-item label="总金额">
          <span class="font-bold text-red-500">¥{{ Number(order.total_amount).toFixed(2) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getOrderStatusType(order.status)">
            {{ (ORDER_STATUS_LABELS as any)[order.status] || order.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="支付状态">
          <el-tag :type="getPaymentStatusType(order.payment_status)">
            {{ (PAYMENT_STATUS_LABELS as any)[order.payment_status] || order.payment_status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ order.shipping_address }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>商品列表</el-divider>

      <el-table :data="order.items" border stripe>
        <el-table-column prop="product.name" label="商品名称" />
        <el-table-column label="下单单价" width="120">
          <template #default="{ row }">¥{{ parseFloat(row.unit_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="小计" width="120">
          <template #default="{ row }">¥{{ parseFloat(row.subtotal).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </div>
    <div v-else class="text-center">
      <p>暂无订单信息</p>
    </div>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import type {Order} from '@/types/order'
import {ORDER_STATUS_LABELS, PAYMENT_STATUS_LABELS} from '@/types/order'

defineProps<{
  modelValue: boolean
  order: Order | null
}>()

defineEmits(['update:modelValue'])

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

const getPaymentStatusType = (status: string) => {
  const types: Record<string, string> = {
    unpaid: 'warning',
    paid: 'success',
    refunded: 'info'
  }
  return types[status] || 'info'
}
</script>

<style scoped>
.order-detail {
  max-height: 60vh;
  overflow-y: auto;
}
</style>