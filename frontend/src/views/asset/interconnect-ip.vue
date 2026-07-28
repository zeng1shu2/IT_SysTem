<template>
  <div class="page-container">
    <!-- Search bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchKeyword" placeholder="IP范围/设备名称" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon> 查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card shadow="never">
      <div class="table-header">
        <span class="table-title">互联IP</span>
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%" @row-dblclick="handleDetail">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="ip_range" label="IP地址范围" min-width="160" />
        <el-table-column prop="source_device_name" label="源设备" min-width="120" />
        <el-table-column prop="source_interface" label="源接口" min-width="140" show-overflow-tooltip />
        <el-table-column prop="dest_device_name" label="目的设备" min-width="120" />
        <el-table-column prop="dest_interface" label="目的接口" min-width="140" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            <span class="text-muted">{{ formatDateTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click.stop="handleDetail(row)">查看</el-button>
            <el-button v-if="userStore.isAdmin" size="small" link @click.stop="handleEdit(row)">编辑</el-button>
            <el-button v-if="userStore.isAdmin" size="small" type="danger" link @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" title="互联IP详情" size="55%">
      <div v-if="detailData" class="detail-body">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="IP地址范围">{{ detailData.ip_range || '—' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detailData.remark || '—' }}</el-descriptions-item>
          <el-descriptions-item label="源设备">{{ detailData.source_device_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="源接口">{{ detailData.source_interface || '—' }}</el-descriptions-item>
          <el-descriptions-item label="目的设备">{{ detailData.dest_device_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="目的接口">{{ detailData.dest_interface || '—' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>

    <!-- Add/Edit Drawer -->
    <el-drawer v-model="dialogVisible" :title="editingId ? '编辑互联IP' : '新增互联IP'" size="50%" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="IP地址范围" required>
          <el-input v-model="editForm.ip_range" placeholder="如：10.0.0.1-10.0.0.10" style="width: 300px" />
        </el-form-item>

        <el-divider content-position="left">源端</el-divider>

        <el-form-item label="源设备">
          <el-select
            v-model="editForm.source_device_id"
            placeholder="选择源设备"
            filterable
            clearable
            style="width: 280px"
            @change="onSourceDeviceChange"
          >
            <el-option
              v-for="asset in assetOptions"
              :key="asset.id"
              :label="asset.device_name"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="源接口">
          <el-select
            v-model="editForm.source_interface"
            placeholder="选择源接口"
            filterable
            clearable
            style="width: 280px"
            :disabled="!sourceInterfaces.length"
          >
            <el-option
              v-for="iface in sourceInterfaces"
              :key="iface.value"
              :label="iface.label"
              :value="iface.value"
            />
          </el-select>
          <span v-if="!sourceInterfaces.length && editForm.source_device_id" class="hint-text">
            该设备暂无端口互联记录
          </span>
        </el-form-item>

        <el-divider content-position="left">目的端</el-divider>

        <el-form-item label="目的设备">
          <el-select
            v-model="editForm.dest_device_id"
            placeholder="选择目的设备"
            filterable
            clearable
            style="width: 280px"
            @change="onDestDeviceChange"
          >
            <el-option
              v-for="asset in assetOptions"
              :key="asset.id"
              :label="asset.device_name"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="目的接口">
          <el-select
            v-model="editForm.dest_interface"
            placeholder="选择目的接口"
            filterable
            clearable
            style="width: 280px"
            :disabled="!destInterfaces.length"
          >
            <el-option
              v-for="iface in destInterfaces"
              :key="iface.value"
              :label="iface.label"
              :value="iface.value"
            />
          </el-select>
          <span v-if="!destInterfaces.length && editForm.dest_device_id" class="hint-text">
            该设备暂无端口互联记录
          </span>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" placeholder="备注信息" style="width: 400px" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getInterconnectIPs, getInterconnectIP, createInterconnectIP, updateInterconnectIP, deleteInterconnectIP } from '@/api/interconnect-ip'
import { getAssets } from '@/api/asset'
import { getPortConnections } from '@/api/port-connection'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const pagination = reactive({ page: 1, size: 20, total: 0 })

const dialogVisible = ref(false)
const editingId = ref(null)
const detailVisible = ref(false)
const detailData = ref(null)

const editForm = reactive({
  ip_range: '',
  source_device_id: null,
  source_device_name: '',
  source_interface: '',
  dest_device_id: null,
  dest_device_name: '',
  dest_interface: '',
  remark: '',
})

// Data for dropdowns
const assetOptions = ref([])
const portConnections = ref([])

// Computed interface lists based on selected device
const sourceInterfaces = computed(() => {
  if (!editForm.source_device_id) return []
  const pc = portConnections.value.find(p => p.asset_id === editForm.source_device_id)
  if (!pc || !pc.ports_data) return []
  return pc.ports_data.map(p => ({
    label: p.name || `端口${p.index}`,
    value: p.name || `端口${p.index}`,
  }))
})

const destInterfaces = computed(() => {
  if (!editForm.dest_device_id) return []
  const pc = portConnections.value.find(p => p.asset_id === editForm.dest_device_id)
  if (!pc || !pc.ports_data) return []
  return pc.ports_data.map(p => ({
    label: p.name || `端口${p.index}`,
    value: p.name || `端口${p.index}`,
  }))
})

function onSourceDeviceChange(assetId) {
  editForm.source_interface = ''
  const asset = assetOptions.value.find(a => a.id === assetId)
  editForm.source_device_name = asset?.device_name || ''
}

function onDestDeviceChange(assetId) {
  editForm.dest_interface = ''
  const asset = assetOptions.value.find(a => a.id === assetId)
  editForm.dest_device_name = asset?.device_name || ''
}

async function loadDropdownData() {
  try {
    const [assetsRes, pcRes] = await Promise.all([
      getAssets({ skip: 0, limit: 1000 }),
      getPortConnections({ skip: 0, limit: 1000 }),
    ])
    assetOptions.value = assetsRes?.items || []
    portConnections.value = pcRes?.items || []
  } catch (err) {
    console.error('Failed to load dropdown data:', err)
    assetOptions.value = []
    portConnections.value = []
  }
}

function formatDateTime(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchData() {
  loading.value = true
  try {
    const data = await getInterconnectIPs({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      keyword: searchKeyword.value || undefined,
    })
    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (err) {
    console.error('Failed to fetch interconnect IPs:', err)
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchKeyword.value = ''
  handleSearch()
}

async function handleAdd() {
  editingId.value = null
  Object.keys(editForm).forEach(k => {
    editForm[k] = k === 'remark' || k === 'ip_range' || k === 'source_interface' || k === 'dest_interface' || k === 'source_device_name' || k === 'dest_device_name' ? '' : null
  })
  await loadDropdownData()
  dialogVisible.value = true
}

async function handleEdit(row) {
  editingId.value = row.id
  await loadDropdownData()
  editForm.ip_range = row.ip_range || ''
  editForm.source_device_id = row.source_device_id || null
  editForm.source_device_name = row.source_device_name || ''
  editForm.source_interface = row.source_interface || ''
  editForm.dest_device_id = row.dest_device_id || null
  editForm.dest_device_name = row.dest_device_name || ''
  editForm.dest_interface = row.dest_interface || ''
  editForm.remark = row.remark || ''
  dialogVisible.value = true
}

async function handleDetail(row) {
  try {
    detailData.value = await getInterconnectIP(row.id)
  } catch {
    detailData.value = row
  }
  detailVisible.value = true
}

async function handleSubmit() {
  if (!editForm.ip_range) {
    ElMessage.warning('请填写IP地址范围')
    return
  }
  const payload = {
    ip_range: editForm.ip_range,
    source_device_id: editForm.source_device_id || null,
    source_device_name: editForm.source_device_name || null,
    source_interface: editForm.source_interface || null,
    dest_device_id: editForm.dest_device_id || null,
    dest_device_name: editForm.dest_device_name || null,
    dest_interface: editForm.dest_interface || null,
    remark: editForm.remark || null,
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await updateInterconnectIP(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createInterconnectIP(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    ElMessage.error('操作失败: ' + (err?.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定要删除「${row.ip_range}」吗？`, '删除确认', { type: 'warning' })
  await deleteInterconnectIP(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
  loadDropdownData()
})
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.search-card :deep(.el-card__body) { padding: 18px 20px 0 20px; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; }
.pagination { margin-top: 16px; justify-content: flex-end; }
.text-muted { color: var(--el-text-color-secondary); font-size: 13px; }
.hint-text { margin-left: 12px; font-size: 12px; color: var(--el-text-color-secondary); }
.detail-body { padding: 0 4px; }
:deep(.el-table__row) { cursor: pointer; }

/* ===== Prevent table cell content from wrapping (use horizontal scroll for overflow) ===== */
:deep(.el-table .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
:deep(.el-table .cell .el-tag) {
  white-space: nowrap;
}
:deep(.el-table) {
  overflow-x: auto;
}
</style>
