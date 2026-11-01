<template>
  <TablePage
    title="商品管理"
    :data="products"
    :loading="loading"
    :total="total"
    :current-page="currentPage"
    :page-size="pageSize"
    @add="openFormDialog()"
    @search="handleSearch"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <el-table-column prop="id" label="ID" min-width="120" show-overflow-tooltip />
    <el-table-column prop="name" label="商品名称" min-width="150" />
    <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
    <el-table-column prop="price" label="价格" width="120">
      <template #default="{ row }">
        <span>¥ {{ parseFloat(row.price).toFixed(2) }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="stock" label="库存" width="100" />
    <el-table-column prop="initial_stock" label="总库存" width="100" />
    <el-table-column prop="created_at" label="创建时间" width="180">
      <template #default="{ row }">
        <span>{{ new Date(row.created_at).toLocaleString() }}</span>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="180" fixed="right">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="openFormDialog(row)">编辑</el-button>
        <el-popconfirm
          title="确定要删除这个商品吗？"
          @confirm="handleDelete(row.id)"
        >
          <template #reference>
            <el-button type="danger" size="small">删除</el-button>
          </template>
        </el-popconfirm>
      </template>
    </el-table-column>
  </TablePage>

  <!-- 表单弹窗 -->
  <el-dialog
    :title="isEditMode ? '编辑商品' : '添加商品'"
    v-model="formDialogVisible"
    width="500px"
    :before-close="closeFormDialog"
  >
    <el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="formData.name" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input type="textarea" v-model="formData.description" />
      </el-form-item>
      <el-form-item label="价格" prop="price">
        <el-input-number v-model="formData.price" :precision="2" :step="0.1" :min="0" />
      </el-form-item>
      <el-form-item label="库存" prop="stock">
        <el-input-number v-model="formData.stock" :min="0" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closeFormDialog">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {onMounted, reactive, ref} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import {type GetProductsParams, productApi, type ProductForm} from '@/api/product'
import type {Product} from '@/types/product'
import TablePage from '@/components/TablePage.vue'

const loading = ref(false)
const products = ref<Product[]>([])

// 分页和搜索
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')

// 表单相关
const formDialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive<ProductForm>({
  name: '',
  description: '',
  price: 0,
  stock: 0
})
const currentProductId = ref<string | null>(null)

const formRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
})

// 获取商品列表
const fetchProducts = async () => {
  loading.value = true
  try {
    const params: GetProductsParams = {
      page: currentPage.value,
      per_page: pageSize.value,
      name: searchQuery.value || undefined
    }
    const response = await productApi.getProducts(params)
    products.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = (query: string) => {
  searchQuery.value = query
  currentPage.value = 1 // 搜索时重置到第一页
  fetchProducts()
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 改变大小后重置到第一页
  fetchProducts()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchProducts()
}

// 打开弹窗
const openFormDialog = (product?: Product) => {
  if (product) {
    isEditMode.value = true
    currentProductId.value = product.id
    Object.assign(formData, {
      name: product.name,
      description: product.description || '',
      price: parseFloat(product.price as any),
      stock: product.stock
    })
  } else {
    isEditMode.value = false
    currentProductId.value = null
    Object.assign(formData, { name: '', description: '', price: 0, stock: 0 })
  }
  formDialogVisible.value = true
}

// 关闭弹窗
const closeFormDialog = () => {
  formDialogVisible.value = false
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditMode.value && currentProductId.value) {
          await productApi.updateProduct(currentProductId.value, formData)
          ElMessage.success('商品更新成功')
        } else {
          await productApi.createProduct(formData)
          ElMessage.success('商品添加成功')
        }
        closeFormDialog()
        fetchProducts() // 重新获取数据，以保证数据最新
      } catch (error) {
        ElMessage.error(isEditMode.value ? '更新失败' : '添加失败')
      }
    }
  })
}

// 删除商品
const handleDelete = async (id: string) => {
  try {
    await productApi.deleteProduct(id)
    ElMessage.success('商品删除成功')
    fetchProducts() // 重新获取数据
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

