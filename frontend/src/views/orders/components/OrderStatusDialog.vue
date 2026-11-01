<template>
  <el-dialog
    title="更新订单状态"
    :model-value="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    width="500px"
    :before-close="handleClose"
  >
    <div v-if="order">
      <p class="mb-4"><strong>订单号:</strong> {{ order.order_number }}</p>
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="订单状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择订单状态">
            <el-option
              v-for="(label, key) in ORDER_STATUS_LABELS"
              :key="key"
              :label="label"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="支付状态" prop="payment_status">
          <el-select v-model="form.payment_status" placeholder="请选择支付状态">
            <el-option
              v-for="(label, key) in PAYMENT_STATUS_LABELS"
              :key="key"
              :label="label"
              :value="key"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确认更新</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {reactive, watch} from 'vue'
import {ElMessage} from 'element-plus'
import type {Order, UpdateOrderForm} from '@/types/order'
import {ORDER_STATUS_LABELS, PAYMENT_STATUS_LABELS} from '@/types/order'
import {orderApi} from '@/api/order'

const props = defineProps<{
  modelValue: boolean
  order: Order | null
}>()

const emit = defineEmits(['update:modelValue', 'success'])

const form = reactive<UpdateOrderForm>({
  status: undefined,
  payment_status: undefined
})

watch(() => props.order, (newOrder) => {
  if (newOrder) {
    form.status = newOrder.status
    form.payment_status = newOrder.payment_status
  }
})

const handleClose = () => {
  emit('update:modelValue', false)
}

const handleSubmit = async () => {
  if (!props.order) return
  try {
    await orderApi.updateOrder(props.order.id, form)
    ElMessage.success('状态更新成功')
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}
</script>