<template>
  <div class="page-container">
    <!-- Search bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchKeyword" placeholder="设备名称" clearable @keyup.enter="handleSearch" />
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
        <span class="table-title">端口互联</span>
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%" @row-dblclick="handleDetail">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="asset_name" label="设备名称" min-width="150" />
        <el-table-column prop="port_count" label="物理端口数" width="100" />
        <el-table-column label="物理端口概况" min-width="180">
          <template #default="{ row }">
            <span v-if="row.ports_data && row.ports_data.length > 0">
              {{ getPortSummary(row.ports_data) }}
            </span>
            <span v-else class="text-muted">未配置</span>
          </template>
        </el-table-column>
        <el-table-column label="逻辑接口数" width="100">
          <template #default="{ row }">
            <span v-if="row.logical_interfaces && row.logical_interfaces.length > 0">
              {{ row.logical_interfaces.length }}
            </span>
            <span v-else class="text-muted">0</span>
          </template>
        </el-table-column>
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
    <el-drawer v-model="detailVisible" title="端口互联详情" size="65%">
      <div v-if="detailData" class="detail-body">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备名称">{{ detailData.asset_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="物理端口数">{{ detailData.port_count }}</el-descriptions-item>
          <el-descriptions-item label="逻辑接口数">{{ (detailData.logical_interfaces || []).length }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detailData.remark || '—' }}</el-descriptions-item>
        </el-descriptions>

        <!-- Physical ports detail -->
        <div v-if="detailData.ports_data && detailData.ports_data.length > 0">
          <div class="section-title">物理端口配置 ({{ detailData.ports_data.length }} 个)</div>
          <el-table :data="detailData.ports_data" border size="small">
            <el-table-column prop="index" label="#" width="50" />
            <el-table-column prop="name" label="端口名称" min-width="140" />
            <el-table-column prop="connected_device" label="对端设备" min-width="120" />
            <el-table-column prop="connected_interface" label="对端接口" min-width="120" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'up' ? 'success' : 'info'" size="small">{{ row.status || '—' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip />
          </el-table>
        </div>

        <!-- Logical interfaces detail -->
        <div v-if="detailData.logical_interfaces && detailData.logical_interfaces.length > 0">
          <div class="section-title">逻辑接口配置 ({{ detailData.logical_interfaces.length }} 个)</div>
          <el-table :data="detailData.logical_interfaces" border size="small">
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'vlanif' ? 'warning' : 'success'" size="small">
                  {{ row.type === 'vlanif' ? 'VLANIF' : 'ETH-TRUNK' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="接口名称" min-width="140" />
            <template v-if="hasVlanif(detailData.logical_interfaces)">
              <el-table-column label="VLAN ID" width="90">
                <template #default="{ row }">{{ row.type === 'vlanif' ? (row.vlan_id || '—') : '—' }}</template>
              </el-table-column>
              <el-table-column label="IP地址" min-width="130">
                <template #default="{ row }">{{ row.type === 'vlanif' ? (row.ip_address || '—') : '—' }}</template>
              </el-table-column>
              <el-table-column label="掩码" min-width="120">
                <template #default="{ row }">{{ row.type === 'vlanif' ? (row.mask || '—') : '—' }}</template>
              </el-table-column>
            </template>
            <template v-if="hasEthTrunk(detailData.logical_interfaces)">
              <el-table-column label="成员端口" min-width="200">
                <template #default="{ row }">
                  <span v-if="row.type === 'eth-trunk' && row.member_ports && row.member_ports.length > 0">
                    {{ row.member_ports.join(', ') }}
                  </span>
                  <span v-else>—</span>
                </template>
              </el-table-column>
            </template>
            <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip />
          </el-table>
        </div>
      </div>
    </el-drawer>

    <!-- Add/Edit Drawer -->
    <el-drawer v-model="dialogVisible" :title="editingId ? '编辑端口互联' : '新增端口互联'" size="75%" :close-on-click-modal="false">
      <el-form label-width="100px">
        <el-form-item label="选择设备" required>
          <el-select
            v-model="selectedAssetId"
            placeholder="选择资产统计中的设备"
            filterable
            style="width: 300px"
            @change="onAssetChange"
          >
            <el-option
              v-for="asset in assetOptions"
              :key="asset.id"
              :label="`${asset.device_name} (${asset.device_type})`"
              :value="asset.id"
            />
          </el-select>
          <span v-if="portCount > 0" class="port-count-tag">
            <el-tag type="info" effect="plain">端口数: {{ portCount }}</el-tag>
          </span>
        </el-form-item>

        <el-form-item label="端口数">
          <el-input-number v-model="portCount" :min="1" :max="999" @change="regeneratePorts" />
          <span class="hint-text">选择设备后自动填充，可手动调整</span>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" placeholder="备注信息" style="width: 400px" />
        </el-form-item>
      </el-form>

      <!-- Physical Port Table -->
      <div v-if="ports.length > 0" class="port-section">
        <div class="port-section-title">
          <span>物理端口配置 (共 {{ ports.length }} 个端口)</span>
        </div>
        <el-table :data="ports" border size="small" style="width: 100%">
          <el-table-column label="#" width="50" type="index" :index="i => i + 1" />
          <el-table-column label="端口名称" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.name" size="small" placeholder="如：GigabitEthernet0/0/1" />
            </template>
          </el-table-column>
          <el-table-column label="对端设备" min-width="180">
            <template #default="{ row }">
              <el-select
                v-model="row.connected_device_id"
                size="small"
                filterable
                clearable
                placeholder="选择对端设备"
                style="width: 100%"
                @change="(val) => onRemoteDeviceChange(row, val)"
              >
                <el-option
                  v-for="asset in remoteDeviceOptions(row)"
                  :key="asset.id"
                  :label="asset.device_name"
                  :value="asset.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="对端接口" min-width="180">
            <template #default="{ row }">
              <el-select
                v-model="row.connected_interface"
                size="small"
                filterable
                clearable
                :placeholder="row.connected_device_id ? '选择对端接口' : '请先选对端设备'"
                :disabled="!row.connected_device_id"
                style="width: 100%"
                @visible-change="(v) => v && loadRemotePorts(row.connected_device_id)"
              >
                <el-option
                  v-for="portName in remotePortOptions(row.connected_device_id)"
                  :key="portName"
                  :label="portName"
                  :value="portName"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-select v-model="row.status" size="small" style="width: 90px">
                <el-option label="Up" value="up" />
                <el-option label="Down" value="down" />
                <el-option label="未连接" value="disconnected" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.remark" size="small" placeholder="备注" />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Logical Interface Section -->
      <div v-if="ports.length > 0" class="port-section">
        <div class="port-section-title">
          <span>逻辑接口配置</span>
          <el-button size="small" type="primary" plain @click="addLogicalInterface">
            <el-icon><Plus /></el-icon> 添加逻辑接口
          </el-button>
        </div>
        <el-table v-if="logicalInterfaces.length > 0" :data="logicalInterfaces" border size="small" style="width: 100%">
          <el-table-column label="类型" width="140">
            <template #default="{ row }">
              <el-select v-model="row.type" size="small" @change="onLogicalTypeChange(row)">
                <el-option label="VLANIF接口" value="vlanif" />
                <el-option label="ETH-TRUNK接口" value="eth-trunk" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="接口名称" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.name" size="small" :placeholder="row.type === 'vlanif' ? '如：Vlanif10' : '如：Eth-Trunk1'" />
            </template>
          </el-table-column>
          <!-- VLANIF fields -->
          <el-table-column v-if="hasVlanif(logicalInterfaces)" label="VLAN ID" width="100">
            <template #default="{ row }">
              <el-input v-if="row.type === 'vlanif'" v-model="row.vlan_id" size="small" placeholder="如：10" />
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="hasVlanif(logicalInterfaces)" label="IP地址" min-width="150">
            <template #default="{ row }">
              <el-input v-if="row.type === 'vlanif'" v-model="row.ip_address" size="small" placeholder="如：192.168.10.1" />
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="hasVlanif(logicalInterfaces)" label="掩码" min-width="140">
            <template #default="{ row }">
              <el-input v-if="row.type === 'vlanif'" v-model="row.mask" size="small" placeholder="如：255.255.255.0" />
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <!-- ETH-TRUNK member ports -->
          <el-table-column v-if="hasEthTrunk(logicalInterfaces)" label="成员端口（关联物理端口）" min-width="280">
            <template #default="{ row }">
              <el-select
                v-if="row.type === 'eth-trunk'"
                v-model="row.member_ports"
                size="small"
                multiple
                filterable
                collapse-tags
                collapse-tags-tooltip
                placeholder="选择物理端口"
                style="width: 100%"
              >
                <el-option
                  v-for="port in ports"
                  :key="port.index"
                  :label="port.name || `端口${port.index}`"
                  :value="port.name || `端口${port.index}`"
                />
              </el-select>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.remark" size="small" placeholder="备注" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70" fixed="right">
            <template #default="{ $index }">
              <el-button size="small" type="danger" link @click="removeLogicalInterface($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无逻辑接口，点击上方按钮添加" :image-size="60" />
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getPortConnections, getPortConnection, getPortConnectionByAssetId, createPortConnection, updatePortConnection, deletePortConnection } from '@/api/port-connection'
import { getAssets } from '@/api/asset'

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

// Form state
const selectedAssetId = ref(null)
const portCount = ref(0)
const ports = ref([])
const logicalInterfaces = ref([])
const editForm = reactive({ remark: '' })

// Asset options for dropdown
const assetOptions = ref([])

// Cache: remote device port lists (asset_id -> port names[])
const remotePortsCache = ref({})

async function loadAssets() {
  try {
    const data = await getAssets({ skip: 0, limit: 1000 })
    assetOptions.value = data.items || []
  } catch (err) {
    console.error('Failed to load assets:', err)
    assetOptions.value = []
  }
}

function onAssetChange(assetId) {
  const asset = assetOptions.value.find(a => a.id === assetId)
  if (asset) {
    const pc = asset.extra_data?.port_count || 24
    portCount.value = pc
    regeneratePorts()
  }
}

function regeneratePorts() {
  const oldPorts = [...ports.value]
  const newPorts = []
  for (let i = 0; i < portCount.value; i++) {
    if (oldPorts[i]) {
      newPorts.push(oldPorts[i])
    } else {
      newPorts.push({
        index: i + 1,
        name: `端口${i + 1}`,
        connected_device_id: null,
        connected_device: '',
        connected_interface: '',
        status: 'disconnected',
        remark: '',
      })
    }
  }
  ports.value = newPorts
}

// ---- Remote device port loading ----

/** Devices available for remote selection (exclude the current device) */
function remoteDeviceOptions(row) {
  return assetOptions.value.filter(a => a.id !== selectedAssetId.value)
}

/** When user selects a remote device, clear the interface and load its ports */
function onRemoteDeviceChange(row, deviceId) {
  row.connected_interface = ''
  const asset = assetOptions.value.find(a => a.id === deviceId)
  row.connected_device = asset ? asset.device_name : ''
  if (deviceId) {
    loadRemotePorts(deviceId)
  }
}

/** Load port names for a remote device (from its port-connection config) */
async function loadRemotePorts(deviceId) {
  if (!deviceId) return
  if (remotePortsCache.value[deviceId]) return // use cache

  try {
    const pcData = await getPortConnectionByAssetId(deviceId)
    const portNames = (pcData.ports_data || [])
      .map(p => p.name)
      .filter(n => n && n.trim())
    remotePortsCache.value[deviceId] = portNames
  } catch {
    // 404 = no port config for this device yet
    remotePortsCache.value[deviceId] = []
  }
}

/** Get port name options for a remote device */
function remotePortOptions(deviceId) {
  return remotePortsCache.value[deviceId] || []
}

// ---- Logical interfaces ----

function addLogicalInterface() {
  logicalInterfaces.value.push({
    type: 'vlanif',
    name: '',
    vlan_id: '',
    ip_address: '',
    mask: '',
    member_ports: [],
    remark: '',
  })
}

function removeLogicalInterface(index) {
  logicalInterfaces.value.splice(index, 1)
}

function onLogicalTypeChange(row) {
  // Clear type-specific fields when switching type
  if (row.type === 'vlanif') {
    row.member_ports = []
  } else if (row.type === 'eth-trunk') {
    row.vlan_id = ''
    row.ip_address = ''
    row.mask = ''
  }
}

function hasVlanif(list) {
  return list.some(item => item.type === 'vlanif')
}

function hasEthTrunk(list) {
  return list.some(item => item.type === 'eth-trunk')
}

// ---- Helpers ----

function getPortSummary(portsData) {
  if (!portsData || portsData.length === 0) return '未配置'
  const connected = portsData.filter(p => p.connected_device).length
  return `${portsData.length} 端口, ${connected} 已互联`
}

function formatDateTime(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ---- Data operations ----

async function fetchData() {
  loading.value = true
  try {
    const data = await getPortConnections({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      keyword: searchKeyword.value || undefined,
    })
    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (err) {
    console.error('Failed to fetch port connections:', err)
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

function handleAdd() {
  editingId.value = null
  selectedAssetId.value = null
  portCount.value = 0
  ports.value = []
  logicalInterfaces.value = []
  remotePortsCache.value = {}
  editForm.remark = ''
  loadAssets()
  dialogVisible.value = true
}

async function handleEdit(row) {
  editingId.value = row.id
  await loadAssets()
  selectedAssetId.value = row.asset_id
  portCount.value = row.port_count || 0
  ports.value = (row.ports_data || []).map((p, i) => ({
    ...p,
    index: i + 1,
    connected_device_id: p.connected_device_id || null,
    connected_device: p.connected_device || '',
    connected_interface: p.connected_interface || '',
  }))
  logicalInterfaces.value = (row.logical_interfaces || []).map(li => ({
    type: li.type || 'vlanif',
    name: li.name || '',
    vlan_id: li.vlan_id || '',
    ip_address: li.ip_address || '',
    mask: li.mask || '',
    member_ports: li.member_ports || [],
    remark: li.remark || '',
  }))
  editForm.remark = row.remark || ''
  remotePortsCache.value = {}

  // Pre-load remote ports for all connected devices
  const deviceIds = [...new Set(ports.value.map(p => p.connected_device_id).filter(Boolean))]
  await Promise.all(deviceIds.map(id => loadRemotePorts(id)))

  dialogVisible.value = true
}

async function handleDetail(row) {
  try {
    detailData.value = await getPortConnection(row.id)
  } catch {
    detailData.value = row
  }
  detailVisible.value = true
}

async function handleSubmit() {
  if (!selectedAssetId.value) {
    ElMessage.warning('请选择设备')
    return
  }
  const asset = assetOptions.value.find(a => a.id === selectedAssetId.value)
  const payload = {
    asset_id: selectedAssetId.value,
    asset_name: asset?.device_name || '',
    port_count: portCount.value,
    ports_data: ports.value.map((p, i) => ({
      index: i + 1,
      name: p.name || `端口${i + 1}`,
      connected_device_id: p.connected_device_id || null,
      connected_device: p.connected_device || '',
      connected_interface: p.connected_interface || '',
      status: p.status || 'disconnected',
      remark: p.remark || '',
    })),
    logical_interfaces: logicalInterfaces.value.map(li => ({
      type: li.type || 'vlanif',
      name: li.name || '',
      vlan_id: li.type === 'vlanif' ? (li.vlan_id || '') : '',
      ip_address: li.type === 'vlanif' ? (li.ip_address || '') : '',
      mask: li.type === 'vlanif' ? (li.mask || '') : '',
      member_ports: li.type === 'eth-trunk' ? (li.member_ports || []) : [],
      remark: li.remark || '',
    })),
    remark: editForm.remark || null,
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await updatePortConnection(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createPortConnection(payload)
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
  await ElMessageBox.confirm(`确定要删除「${row.asset_name || 'ID:' + row.id}」的端口互联吗？`, '删除确认', { type: 'warning' })
  await deletePortConnection(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.search-card :deep(.el-card__body) { padding: 18px 20px 0 20px; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; }
.pagination { margin-top: 16px; justify-content: flex-end; }
.text-muted { color: var(--el-text-color-secondary); font-size: 13px; }
.port-count-tag { margin-left: 12px; }
.hint-text { margin-left: 12px; font-size: 12px; color: var(--el-text-color-secondary); }
.detail-body { padding: 0 4px; display: flex; flex-direction: column; gap: 20px; }
.section-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.port-section { margin-top: 20px; }
.port-section-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; display: flex; align-items: center; gap: 12px; }
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
