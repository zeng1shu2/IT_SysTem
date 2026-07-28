<template>
  <div class="page-container">
    <!-- Permission catalog & apply -->
    <el-card shadow="never" class="search-card">
      <div class="table-header">
        <span class="table-title">权限申请</span>
        <el-button type="primary" @click="handleApply">
          <el-icon><Plus /></el-icon> 申请权限
        </el-button>
      </div>
      <div class="catalog-grid">
        <el-card v-for="perm in catalog" :key="perm.code" shadow="hover" class="perm-card">
          <div class="perm-info">
            <div class="perm-name">{{ perm.name }}</div>
            <div class="perm-desc">{{ perm.description }}</div>
            <el-tag size="small" type="info">{{ perm.code }}</el-tag>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- Request history -->
    <el-card shadow="never">
      <div class="table-header">
        <span class="table-title">申请记录</span>
        <el-button @click="fetchRequests"><el-icon><Refresh /></el-icon> 刷新</el-button>
      </div>
      <el-table :data="requestList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="申请人" width="120" />
        <el-table-column prop="permission_code" label="权限编码" width="140" />
        <el-table-column prop="reason" label="申请理由" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : 'danger'">
              {{ row.status === 'approved' ? '已批准' : '已拒绝' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="auto_rule" label="匹配规则" width="160" />
        <el-table-column prop="approved_at" label="审批时间" width="170">
          <template #default="{ row }">{{ formatTime(row.approved_at) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, prev, pager, next"
        class="pagination"
        @size-change="fetchRequests"
        @current-change="fetchRequests"
      />
    </el-card>

    <!-- Apply dialog -->
    <el-dialog v-model="applyDialog" title="申请权限" width="480px">
      <el-form ref="formRef" :model="applyForm" :rules="applyRules" label-width="80px">
        <el-form-item label="权限" prop="permission_code">
          <el-select v-model="applyForm.permission_code" style="width: 100%" placeholder="选择权限">
            <el-option v-for="p in catalog" :key="p.code" :label="`${p.name} (${p.code})`" :value="p.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请理由">
          <el-input v-model="applyForm.reason" type="textarea" :rows="3" placeholder="请输入申请理由（选填）" />
        </el-form-item>
      </el-form>
      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 12px">
        系统将根据预设规则自动审批：查看类权限自动批准，管理类权限需管理员身份。
      </el-alert>
      <template #footer>
        <el-button @click="applyDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitApply">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPermissionCatalog, getPermissionRequests, applyPermission } from '@/api/permission'

const loading = ref(false)
const submitting = ref(false)
const catalog = ref([])
const requestList = ref([])
const applyDialog = ref(false)
const formRef = ref()
const pagination = reactive({ page: 1, size: 20, total: 0 })

const applyForm = reactive({ permission_code: '', reason: '' })
const applyRules = {
  permission_code: [{ required: true, message: '请选择权限', trigger: 'change' }],
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function fetchCatalog() {
  catalog.value = await getPermissionCatalog()
}

async function fetchRequests() {
  loading.value = true
  try {
    const data = await getPermissionRequests({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
    })
    requestList.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

function handleApply() {
  applyForm.permission_code = ''
  applyForm.reason = ''
  applyDialog.value = true
}

async function submitApply() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const result = await applyPermission(applyForm)
      ElMessage.success(result.status === 'approved' ? '权限已自动批准' : '权限申请已被拒绝')
      applyDialog.value = false
      fetchRequests()
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  fetchCatalog()
  fetchRequests()
})
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; }
.catalog-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.perm-card { cursor: default; }
.perm-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.perm-desc { font-size: 12px; color: #909399; margin-bottom: 8px; }
.pagination { margin-top: 16px; justify-content: flex-end; }
</style>
