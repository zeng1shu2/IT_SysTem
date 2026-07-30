<template>
  <div class="page-container">
    <el-card shadow="never">
      <div class="table-header">
        <span class="table-title">角色列表</span>
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增角色</el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="角色名称" width="140" />
        <el-table-column prop="code" label="角色编码" width="140" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="permissions" label="权限" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="p in row.permissions" :key="p" size="small" class="perm-tag">{{ p }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, prev, pager, next"
        class="pagination"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑角色' : '新增角色'" width="540px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="角色名称" prop="name"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="角色编码" prop="code"><el-input v-model="formData.code" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="formData.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="权限">
          <el-select v-model="formData.permissions" multiple filterable style="width: 100%" placeholder="选择权限">
            <el-option v-for="p in permissionCatalog" :key="p.code" :label="`${p.name} (${p.code})`" :value="p.code" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole } from '@/api/role'
import { getPermissionCatalog } from '@/api/permission'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const permissionCatalog = ref([])

const pagination = reactive({ page: 1, size: 20, total: 0 })
const defaultForm = { name: '', code: '', description: '', permissions: [] }
const formData = reactive({ ...defaultForm })

const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }

async function fetchData() {
  loading.value = true
  try {
    const data = await getRoles({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
    })
    tableData.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

async function fetchCatalog() {
  permissionCatalog.value = await getPermissionCatalog()
}

function handleAdd() {
  editingId.value = null
  Object.assign(formData, { ...defaultForm, permissions: [] })
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.assign(formData, {
    name: row.name, code: row.code, description: row.description,
    permissions: [...(row.permissions || [])],
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editingId.value) {
        await updateRole(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createRole(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定要删除角色「${row.name}」吗？`, '删除确认', { type: 'warning' })
  await deleteRole(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
  fetchCatalog()
})
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; }
.perm-tag { margin: 2px; }
.pagination { margin-top: 16px; justify-content: flex-end; }
</style>
