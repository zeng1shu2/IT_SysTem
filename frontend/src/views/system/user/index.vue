<template>
  <div class="page-container">
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="用户名/姓名/邮箱" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon> 查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <div class="table-header">
        <span class="table-title">用户列表</span>
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增用户</el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="email" label="邮箱" min-width="160" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="is_admin" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">{{ row.is_admin ? '管理员' : '普通' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="170">
          <template #default="{ row }">{{ formatTime(row.last_login_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleResetPwd(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>

    <!-- Add/Edit dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新增用户'" width="540px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item v-if="!editingId" label="密码" prop="password">
          <el-input v-model="formData.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="formData.real_name" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="formData.email" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="formData.phone" /></el-form-item>
        <el-form-item label="部门"><el-input v-model="formData.department" /></el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="formData.is_admin" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Reset password dialog -->
    <el-dialog v-model="pwdDialog" title="重置密码" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="100px">
        <el-form-item label="用户"><el-input :model-value="pwdForm.username" disabled /></el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitResetPwd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser, resetPassword } from '@/api/user'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const pwdDialog = ref(false)
const editingId = ref(null)
const formRef = ref()
const pwdFormRef = ref()

const searchForm = reactive({ keyword: '', is_active: undefined })
const pagination = reactive({ page: 1, size: 20, total: 0 })

const defaultForm = {
  username: '', password: '', real_name: '', email: '',
  phone: '', department: '', is_admin: false, is_active: true,
}
const formData = reactive({ ...defaultForm })
const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6, message: '密码至少6位' }],
}

const pwdForm = reactive({ username: '', new_password: '' })
const pwdRules = {
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码至少6位' }],
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function fetchData() {
  loading.value = true
  try {
    const data = await getUsers({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      keyword: searchForm.keyword || undefined,
      is_active: searchForm.is_active,
    })
    tableData.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() { pagination.page = 1; fetchData() }
function handleReset() { searchForm.keyword = ''; searchForm.is_active = undefined; handleSearch() }

function handleAdd() {
  editingId.value = null
  Object.assign(formData, defaultForm)
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.assign(formData, {
    username: row.username, real_name: row.real_name, email: row.email,
    phone: row.phone, department: row.department, is_admin: row.is_admin, is_active: row.is_active,
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
        const { username, password, ...updateData } = formData
        await updateUser(editingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await createUser(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      submitting.value = false
    }
  })
}

function handleResetPwd(row) {
  pwdForm.username = row.username
  pwdForm.new_password = ''
  pwdDialog.value = true
}

async function submitResetPwd() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      // Find user id from tableData
      const user = tableData.value.find((u) => u.username === pwdForm.username)
      if (user) {
        await resetPassword(user.id, { new_password: pwdForm.new_password })
        ElMessage.success('密码已重置')
        pwdDialog.value = false
      }
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定要删除用户「${row.username}」吗？`, '删除确认', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.search-card :deep(.el-card__body) { padding: 18px 20px 0 20px; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; }
.pagination { margin-top: 16px; justify-content: flex-end; }
</style>
