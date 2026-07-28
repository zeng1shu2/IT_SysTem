<template>
  <div class="page-container">
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" @submit.prevent>
        <el-form-item label="操作人">
          <el-input v-model="searchForm.operator" placeholder="操作人用户名" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.operation_type" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="t in opTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="对象类型">
          <el-select v-model="searchForm.target_type" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="t in targetTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="结果">
          <el-select v-model="searchForm.result" placeholder="全部" clearable style="width: 100px">
            <el-option label="成功" :value="true" />
            <el-option label="失败" :value="false" />
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
        <span class="table-title">审计日志</span>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="operator_ip" label="操作IP" width="140" />
        <el-table-column prop="operation_time" label="操作时间" width="170">
          <template #default="{ row }">{{ formatTime(row.operation_time) }}</template>
        </el-table-column>
        <el-table-column prop="operation_type" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="opTypeTag(row.operation_type)" size="small">{{ opTypeLabel(row.operation_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="对象类型" width="100">
          <template #default="{ row }">{{ targetTypeLabel(row.target_type) }}</template>
        </el-table-column>
        <el-table-column prop="target_id" label="对象ID" width="80" />
        <el-table-column prop="result" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.result ? 'success' : 'danger'" size="small">{{ row.result ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="变更详情" min-width="250" show-overflow-tooltip />
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAuditLogs } from '@/api/audit'

const loading = ref(false)
const tableData = ref([])

const opTypes = [
  { label: '登录', value: 'login' }, { label: '登出', value: 'logout' },
  { label: '新增', value: 'create' }, { label: '更新', value: 'update' },
  { label: '删除', value: 'delete' }, { label: '审批', value: 'approve' },
  { label: '查询', value: 'query' },
]
const targetTypes = [
  { label: '系统', value: 'system' }, { label: '用户', value: 'user' },
  { label: '角色', value: 'role' }, { label: '资产', value: 'asset' },
  { label: '权限', value: 'permission' },
]

const searchForm = reactive({ operator: '', operation_type: '', target_type: '', result: undefined })
const pagination = reactive({ page: 1, size: 20, total: 0 })

function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }
function opTypeLabel(v) { return opTypes.find((t) => t.value === v)?.label || v }
function opTypeTag(v) {
  const map = { login: 'success', logout: 'info', create: 'primary', update: 'warning', delete: 'danger', approve: '', query: 'info' }
  return map[v] || ''
}
function targetTypeLabel(v) { return targetTypes.find((t) => t.value === v)?.label || v || '-' }

async function fetchData() {
  loading.value = true
  try {
    const data = await getAuditLogs({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      operator: searchForm.operator || undefined,
      operation_type: searchForm.operation_type || undefined,
      target_type: searchForm.target_type || undefined,
      result: searchForm.result,
    })
    tableData.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() { pagination.page = 1; fetchData() }
function handleReset() {
  searchForm.operator = ''; searchForm.operation_type = ''; searchForm.target_type = ''; searchForm.result = undefined
  handleSearch()
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
