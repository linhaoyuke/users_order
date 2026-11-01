<template>
  <el-dialog
    :title="isEditMode ? '编辑订单' : '创建新订单'"
    :model-value="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    width="800px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="选择用户" prop="user_id">
        <el-select
          v-model="form.user_id"
          placeholder="搜索并选择用户"
          filterable
          remote
          :remote-method="searchUsers"
          :loading="userLoading"
          style="width: 100%;"
          :disabled="isEditMode"
        >
          <el-option
            v-for="user in userList"
            :key="user.id"
            :label="`${user.username} (${user.full_name || 'N/A'}) - ${user.email}`"
            :value="user.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="selectedUserEmail" label="用户邮箱">
        <el-input :value="selectedUserEmail" readonly />
      </el-form-item>

      <el-form-item label="收货地址" prop="shipping_address">
        <el-input type="textarea" v-model="form.shipping_address" />
      </el-form-item>

      <el-divider>订单商品</el-divider>

      <!-- 商品选择器 -->
      <div class="flex gap-2 mb-4">
        <el-select
          v-model="selectedProduct"
          placeholder="搜索并选择商品"
          filterable
          remote
          :remote-method="searchProducts"
          :loading="productLoading"
          class="flex-grow"
          value-key="id"
          clearable
        >
          <el-option
            v-for="product in productList"
            :key="product.id"
            :label="`${product.name} (¥${product.price} / 库存: ${product.stock})`"
            :value="product"
          />
        </el-select>
        <el-input-number v-model="selectedQuantity" :min="1" class="w-32" />
        <el-button type="primary" @click="addOrderItem" :disabled="!selectedProduct">添加商品</el-button>
      </div>

      <!-- 订单项表格 -->
      <el-table :data="form.items" border stripe>
        <el-table-column prop="product.name" label="商品名称" />
        <el-table-column label="单价">
          <template #default="{ row }">¥{{ row.product.price }}</template>
        </el-table-column>
        <el-table-column label="数量">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" :max="row.product.stock" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="小计">
          <template #default="{ row }">¥{{ (row.product.price * row.quantity).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeOrderItem($index)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="text-right mt-4 text-xl font-bold">
        总计: ¥{{ totalAmount.toFixed(2) }}
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="submitForm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {computed, reactive, ref, watch} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import type {CreateOrderForm, Order, UpdateOrderForm} from '@/types/order'
import type {Product} from '@/types/product'
import type {User} from '@/types/user'
import {orderApi} from '@/api/order'
import {productApi} from '@/api/product'
import {userApi} from '@/api/user'

const props = defineProps<{
  modelValue: boolean
  order: Order | null
}>()

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref<FormInstance>()
const isEditMode = ref(false)

// 表单数据
const form = reactive<{
  user_id: number | null
  shipping_address: string
  items: { product: Product; quantity: number }[]
}>({
  user_id: null,
  shipping_address: '',
  items: []
})

// 用户搜索
const userLoading = ref(false)
const userList = ref<User[]>([])

// 商品搜索
const productLoading = ref(false)
const productList = ref<Product[]>([])
const selectedProduct = ref<Product | null>(null)
const selectedQuantity = ref(1)

const rules = reactive<FormRules>({
  user_id: [{ required: true, message: '请选择一个用户', trigger: 'change' }],
  items: [{ required: true, type: 'array', min: 1, message: '请至少添加一个商品', trigger: 'change' }]
})

// 计算总金额
const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + Number(item.product.price) * item.quantity, 0)
})

// 获取选中用户的邮箱
const selectedUserEmail = computed(() => {
  if (form.user_id) {
    const selectedUser = allUsers.value.find(user => user.id === form.user_id)
    return selectedUser ? selectedUser.email : ''
  }
  return ''
})

const allUsers = ref<User[]>([]) // 缓存所有用户

// ... (其他 ref 定义)

// 监控对话框的显示状态
watch(() => props.modelValue, (isVisible) => {
  if (isVisible && !isEditMode.value) {
    // 当对话框打开且是创建模式时，加载所有用户
    loadAllUsers()
  }
})

// 监控 props.order 的变化来填充表单
watch(() => props.order, (newOrder) => {
  isEditMode.value = !!newOrder
  if (newOrder) {
    form.user_id = newOrder.user_id
    form.shipping_address = newOrder.shipping_address || ''
    form.items = newOrder.items.map(item => ({
      product: item.product,
      quantity: item.quantity
    }))
    // 如果是编辑模式，预加载当前用户到列表
    if (newOrder.user_id && (newOrder as any).user) {
      userList.value = [(newOrder as any).user]
    }
  } else {
    // 重置表单
    form.user_id = null
    form.shipping_address = ''
    form.items = []
    userList.value = []
  }
})

// 加载所有用户到缓存
const loadAllUsers = async () => {
  if (allUsers.value.length > 0) return // 避免重复加载
  userLoading.value = true
  try {
    const response = await userApi.getAllUsers()
    allUsers.value = response.data
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    userLoading.value = false
  }
}

// 在本地进行用户搜索
const searchUsers = (query: string) => {
  if (query && query.length >= 2) {
    userList.value = allUsers.value.filter(user => 
      user.username.toLowerCase().includes(query.toLowerCase()) ||
      (user.full_name && user.full_name.toLowerCase().includes(query.toLowerCase()))
    )
  } else {
    userList.value = [] // 如果查询词太短，则清空列表
  }
}

// 搜索商品
const searchProducts = async (query: string) => {
  if (query) {
    productLoading.value = true
    try {
      const response = await productApi.getProducts({ name: query }) // 假设API支持按名称搜索
      productList.value = response.data.items
    } catch (error) {
      productList.value = []
    } finally {
      productLoading.value = false
    }
  } else {
    productList.value = []
  }
}

// 添加商品到订单
const addOrderItem = () => {
  if (!selectedProduct.value) {
    ElMessage.warning('请先选择一个商品')
    return
  }
  // 检查是否已存在
  const existingItem = form.items.find(item => item.product.id === selectedProduct.value!.id)
  if (existingItem) {
    existingItem.quantity += selectedQuantity.value
  } else {
    form.items.push({
      product: selectedProduct.value,
      quantity: selectedQuantity.value
    })
  }
  // 重置选择器
  selectedProduct.value = null
  selectedQuantity.value = 1
  productList.value = []
}

// 移除订单中的商品
const removeOrderItem = (index: number) => {
  form.items.splice(index, 1)
}

// 关闭对话框
const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:modelValue', false)
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (isEditMode.value) {
        // 编辑逻辑
        const updateData: UpdateOrderForm = {
          shipping_address: form.shipping_address,
          items: form.items.map(item => ({
            product_id: item.product.id,
            quantity: item.quantity
          }))
        }
        console.log('提交的更新数据:', updateData)
        console.log('form.items:', form.items)
        console.log('items数量:', form.items.length)
        console.log('订单ID:', props.order!.id)
        console.log('编辑模式:', isEditMode.value)
        try {
          await orderApi.updateOrder(props.order!.id, updateData)
          ElMessage.success('订单更新成功')
          emit('success')
          handleClose()
        } catch (error) {
          ElMessage.error('订单更新失败')
        }
      } else {
        // 创建逻辑
        const createData: CreateOrderForm = {
          user_id: form.user_id,
          shipping_address: form.shipping_address,
          items: form.items.map(item => ({
            product_id: item.product.id,
            quantity: item.quantity
          }))
        }
        try {
          await orderApi.createOrder(createData)
          ElMessage.success('订单创建成功')
          emit('success')
          handleClose()
        } catch (error) {
          ElMessage.error('订单创建失败')
        }
      }
    }
  })
}
</script>