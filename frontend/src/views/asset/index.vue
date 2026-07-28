<template>
  <div class="page-container">
    <!-- Search bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="设备名称/IP/序列号" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="searchForm.device_type" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="item in deviceTypes" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card shadow="never" class="table-card">
      <div class="table-header">
        <span class="table-title">网络设备列表</span>
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增设备
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="device_name" label="设备名称" min-width="120" />
        <el-table-column prop="device_type" label="类型" width="100">
          <template #default="{ row }">{{ deviceTypeLabel(row.device_type) }}</template>
        </el-table-column>
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="ip_address" label="管理IP" width="140" />
        <el-table-column prop="location" label="位置" min-width="120" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="userStore.isAdmin" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- ==================== Add/Edit Drawer with Live Preview ==================== -->
    <el-drawer
      v-model="dialogVisible"
      :title="editingId ? '编辑设备' : '新增设备'"
      size="75%"
      :close-on-click-modal="false"
    >
      <div class="drawer-body">
        <!-- ===== Left: Form ===== -->
        <div class="form-panel">
          <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" label-position="right">
            <!-- 基础信息 -->
            <div class="form-section-title">基础信息</div>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="设备名称" prop="device_name">
                  <el-input v-model="formData.device_name" placeholder="如：核心交换机-01" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="设备类型" prop="device_type">
                  <el-select v-model="formData.device_type" style="width: 100%" @change="onDeviceTypeChange">
                    <el-option v-for="item in deviceTypes" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="品牌"><el-input v-model="formData.brand" placeholder="如：华为" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="型号"><el-input v-model="formData.model" placeholder="如：S5700-28C-HI" /></el-form-item>
              </el-col>
            </el-row>

            <!-- 网络信息 -->
            <div class="form-section-title">网络信息</div>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="管理IP" prop="ip_address">
                  <el-input
                    v-model="formData.ip_address"
                    placeholder="如：192.168.1.1"
                    :class="{ 'input-error': ipError, 'input-valid': ipValid }"
                  />
                  <div v-if="ipError" class="field-hint error">{{ ipError }}</div>
                  <div v-else-if="ipValid" class="field-hint success">IP 格式正确</div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="MAC地址" prop="mac_address">
                  <el-input
                    v-model="formData.mac_address"
                    placeholder="如：00:1A:2B:3C:4D:5E"
                    :class="{ 'input-error': macError, 'input-valid': macValid }"
                  />
                  <div v-if="macError" class="field-hint error">{{ macError }}</div>
                  <div v-else-if="macValid" class="field-hint success">MAC 格式正确</div>
                </el-form-item>
              </el-col>
            </el-row>

            <!-- ===== 动态字段：根据设备类型显示不同字段 ===== -->
            <div class="form-section-title">
              {{ dynamicSectionTitle }}
              <el-tag size="small" type="warning" effect="plain" class="dynamic-tag">动态字段</el-tag>
            </div>

            <!-- 交换机：端口数 + VLAN范围 -->
            <template v-if="formData.device_type === 'switch'">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="端口数">
                    <el-input-number v-model="formData.dynamic.port_count" :min="1" :max="9999" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="VLAN范围">
                    <el-input v-model="formData.dynamic.vlan_range" placeholder="如：1-100, 200" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- 路由器：协议 + WAN口数 -->
            <template v-else-if="formData.device_type === 'router'">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="路由协议">
                    <el-select v-model="formData.dynamic.protocol" style="width: 100%" multiple collapse-tags>
                      <el-option label="OSPF" value="ospf" />
                      <el-option label="BGP" value="bgp" />
                      <el-option label="RIP" value="rip" />
                      <el-option label="静态路由" value="static" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="WAN口数">
                    <el-input-number v-model="formData.dynamic.wan_count" :min="1" :max="16" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- 防火墙：安全域 + 策略数 -->
            <template v-else-if="formData.device_type === 'firewall'">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="安全域">
                    <el-select v-model="formData.dynamic.security_zone" style="width: 100%">
                      <el-option label="Trust（信任）" value="trust" />
                      <el-option label="Untrust（不信任）" value="untrust" />
                      <el-option label="DMZ（隔离区）" value="dmz" />
                      <el-option label="自定义" value="custom" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="策略数">
                    <el-input-number v-model="formData.dynamic.policy_count" :min="0" :max="9999" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- 安全设备：设备子类 + 防护级别 -->
            <template v-else-if="formData.device_type === 'security'">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="安全子类">
                    <el-select v-model="formData.dynamic.sub_type" style="width: 100%">
                      <el-option label="IDS（入侵检测）" value="ids" />
                      <el-option label="IPS（入侵防御）" value="ips" />
                      <el-option label="WAF（Web应用防火墙）" value="waf" />
                      <el-option label="上网行为管理" value="behavior" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="防护级别">
                    <el-rate v-model="formData.dynamic.protection_level" :max="5" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- 其他设备：自定义描述 -->
            <template v-else>
              <el-form-item label="设备描述">
                <el-input v-model="formData.dynamic.description" type="textarea" :rows="2" placeholder="请描述设备用途..." />
              </el-form-item>
            </template>

            <!-- 位置与状态 -->
            <div class="form-section-title">位置与状态</div>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="序列号"><el-input v-model="formData.serial_number" placeholder="设备序列号" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="状态">
                  <el-select v-model="formData.status" style="width: 100%">
                    <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="存放位置"><el-input v-model="formData.location" placeholder="如：机房A-机柜03-U12" /></el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="采购日期">
                  <el-date-picker v-model="formData.purchase_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="保修到期">
                  <el-date-picker v-model="formData.warranty_expire" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="备注"><el-input v-model="formData.remark" type="textarea" :rows="2" /></el-form-item>
          </el-form>
        </div>

        <!-- ===== Right: Live Preview ===== -->
        <div class="preview-panel">
          <div class="preview-header">
            <el-icon><View /></el-icon>
            <span>实时预览</span>
            <el-tag size="small" type="success" effect="dark">LIVE</el-tag>
          </div>
          <div class="preview-card">
            <!-- 设备图标 + 状态 -->
            <div class="preview-top">
              <div class="preview-icon" :style="{ background: deviceTypeColor(formData.device_type) }">
                <span>{{ deviceTypeEmoji(formData.device_type) }}</span>
              </div>
              <div class="preview-name-area">
                <div class="preview-device-name">{{ formData.device_name || '未命名设备' }}</div>
                <div class="preview-device-type">{{ deviceTypeLabel(formData.device_type) }} · {{ formData.brand || '未知品牌' }}</div>
              </div>
              <el-tag :type="statusTagType(formData.status)" effect="dark" size="small">
                {{ statusLabel(formData.status) }}
              </el-tag>
            </div>

            <!-- 核心信息 -->
            <div class="preview-info-grid">
              <div class="preview-info-item">
                <span class="info-label">型号</span>
                <span class="info-value">{{ formData.model || '—' }}</span>
              </div>
              <div class="preview-info-item">
                <span class="info-label">带外管理IP</span>
                <span class="info-value" :class="{ 'ip-valid-text': ipValid, 'ip-error-text': ipError }">
                  {{ formData.ip_address || '—' }}
                </span>
              </div>
              <div class="preview-info-item">
                <span class="info-label">MAC地址</span>
                <span class="info-value" :class="{ 'ip-valid-text': macValid, 'ip-error-text': macError }">
                  {{ formData.mac_address || '—' }}
                </span>
              </div>
              <div class="preview-info-item">
                <span class="info-label">序列号</span>
                <span class="info-value">{{ formData.serial_number || '—' }}</span>
              </div>
              <div class="preview-info-item">
                <span class="info-label">存放位置</span>
                <span class="info-value">{{ formData.location || '—' }}</span>
              </div>
            </div>

            <!-- 动态字段预览 -->
            <div class="preview-dynamic">
              <div class="preview-dynamic-title">设备特性（{{ dynamicSectionTitle }}）</div>
              <template v-if="formData.device_type === 'switch'">
                <div class="preview-tag-row">
                  <el-tag size="small">端口数: {{ formData.dynamic.port_count }}</el-tag>
                  <el-tag size="small" v-if="formData.dynamic.vlan_range">VLAN: {{ formData.dynamic.vlan_range }}</el-tag>
                </div>
              </template>
              <template v-else-if="formData.device_type === 'router'">
                <div class="preview-tag-row">
                  <el-tag size="small" v-for="p in formData.dynamic.protocol" :key="p" type="warning">
                    {{ protocolLabel(p) }}
                  </el-tag>
                  <el-tag size="small">WAN口: {{ formData.dynamic.wan_count }}</el-tag>
                </div>
              </template>
              <template v-else-if="formData.device_type === 'firewall'">
                <div class="preview-tag-row">
                  <el-tag size="small" type="danger">安全域: {{ securityZoneLabel(formData.dynamic.security_zone) }}</el-tag>
                  <el-tag size="small">策略数: {{ formData.dynamic.policy_count }}</el-tag>
                </div>
              </template>
              <template v-else-if="formData.device_type === 'security'">
                <div class="preview-tag-row">
                  <el-tag size="small" type="warning">{{ securitySubLabel(formData.dynamic.sub_type) }}</el-tag>
                  <el-tag size="small" type="success">防护: {{ '★'.repeat(formData.dynamic.protection_level) || '未设置' }}</el-tag>
                </div>
              </template>
              <template v-else>
                <div class="preview-desc">{{ formData.dynamic.description || '暂无描述' }}</div>
              </template>
            </div>

            <!-- 日期信息 -->
            <div class="preview-dates" v-if="formData.purchase_date || formData.warranty_expire">
              <div v-if="formData.purchase_date">采购: {{ formData.purchase_date }}</div>
              <div v-if="formData.warranty_expire">保修至: {{ formData.warranty_expire }}</div>
            </div>

            <!-- 备注 -->
            <div class="preview-remark" v-if="formData.remark">
              <span class="remark-label">备注</span>
              <span class="remark-text">{{ formData.remark }}</span>
            </div>

            <!-- 完整度指示器 -->
            <div class="preview-completeness">
              <div class="completeness-label">
                <span>信息完整度</span>
                <span class="completeness-value">{{ completeness }}%</span>
              </div>
              <el-progress :percentage="completeness" :color="completenessColor" :show-text="false" :stroke-width="6" />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, View } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getAssets, createAsset, updateAsset, deleteAsset } from '@/api/asset'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()

const deviceTypes = [
  { label: '交换机', value: 'switch' },
  { label: '路由器', value: 'router' },
  { label: '防火墙', value: 'firewall' },
  { label: '安全设备', value: 'security' },
  { label: '其他设备', value: 'other' },
]

const statusOptions = [
  { label: '使用中', value: 'in_use' },
  { label: '空闲', value: 'idle' },
  { label: '故障', value: 'fault' },
  { label: '维护中', value: 'maintenance' },
  { label: '已报废', value: 'scrap' },
]

const searchForm = reactive({ keyword: '', device_type: '', status: '' })
const pagination = reactive({ page: 1, size: 20, total: 0 })

const defaultForm = {
  device_name: '', device_type: 'switch', brand: '', model: '',
  serial_number: '', ip_address: '', mac_address: '', location: '',
  status: 'in_use', purchase_date: '', warranty_expire: '', remark: '',
  dynamic: { port_count: 24, vlan_range: '', protocol: [], wan_count: 1, security_zone: 'trust', policy_count: 0, sub_type: 'ids', protection_level: 3, description: '' },
}
const formData = reactive(JSON.parse(JSON.stringify(defaultForm)))

const formRules = {
  device_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
}

// ==================== Dynamic Section Title ====================
const dynamicSectionTitle = computed(() => {
  const map = { switch: '交换机特性', router: '路由器特性', firewall: '防火墙特性', security: '安全设备特性', other: '设备描述' }
  return map[formData.device_type] || '设备特性'
})

// ==================== Real-time IP/MAC Validation ====================
const ipValid = computed(() => {
  if (!formData.ip_address) return false
  return /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/.test(formData.ip_address)
})
const ipError = computed(() => {
  if (!formData.ip_address) return ''
  return ipValid.value ? '' : 'IP 地址格式不正确'
})

const macValid = computed(() => {
  if (!formData.mac_address) return false
  return /^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$/.test(formData.mac_address)
})
const macError = computed(() => {
  if (!formData.mac_address) return ''
  return macValid.value ? '' : 'MAC 地址格式不正确（如 00:1A:2B:3C:4D:5E）'
})

// ==================== Completeness Score ====================
const completeness = computed(() => {
  const fields = ['device_name', 'device_type', 'brand', 'model', 'serial_number', 'ip_address', 'mac_address', 'location', 'status']
  let filled = 0
  fields.forEach((f) => { if (formData[f]) filled++ })
  if (ipValid.value) filled += 0.5
  if (macValid.value) filled += 0.5
  if (formData.remark) filled += 0.5
  if (formData.purchase_date) filled += 0.5
  if (formData.warranty_expire) filled += 0.5
  return Math.min(100, Math.round((filled / (fields.length + 2)) * 100))
})
const completenessColor = computed(() => {
  if (completeness.value >= 80) return '#67c23a'
  if (completeness.value >= 50) return '#e6a23c'
  return '#f56c6c'
})

// ==================== Helpers ====================
function deviceTypeLabel(val) {
  return deviceTypes.find((t) => t.value === val)?.label || val
}
function statusLabel(val) {
  return statusOptions.find((s) => s.value === val)?.label || val
}
function statusTagType(val) {
  const map = { in_use: 'success', idle: 'info', fault: 'danger', maintenance: 'warning', scrap: '' }
  return map[val] || ''
}
function deviceTypeColor(val) {
  const map = { switch: '#409eff', router: '#67c23a', firewall: '#f56c6c', security: '#e6a23c', other: '#909399' }
  return map[val] || '#909399'
}
function deviceTypeEmoji(val) {
  const map = { switch: '🔀', router: '📡', firewall: '🛡', security: '🔒', other: '📦' }
  return map[val] || '📦'
}
function protocolLabel(val) {
  const map = { ospf: 'OSPF', bgp: 'BGP', rip: 'RIP', static: '静态路由' }
  return map[val] || val
}
function securityZoneLabel(val) {
  const map = { trust: 'Trust', untrust: 'Untrust', dmz: 'DMZ', custom: '自定义' }
  return map[val] || val
}
function securitySubLabel(val) {
  const map = { ids: '入侵检测', ips: '入侵防御', waf: 'Web防火墙', behavior: '行为管理' }
  return map[val] || val
}

// ==================== Device Type Change Handler ====================
function onDeviceTypeChange() {
  // Reset dynamic fields to defaults when type changes
  const defaults = {
    port_count: 24, vlan_range: '', protocol: [], wan_count: 1,
    security_zone: 'trust', policy_count: 0, sub_type: 'ids', protection_level: 3, description: '',
  }
  Object.assign(formData.dynamic, defaults)
}

// ==================== Data Fetching ====================
async function fetchData() {
  loading.value = true
  try {
    const data = await getAssets({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      keyword: searchForm.keyword || undefined,
      device_type: searchForm.device_type || undefined,
      status: searchForm.status || undefined,
    })
    tableData.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.device_type = ''
  searchForm.status = ''
  handleSearch()
}

function handleAdd() {
  editingId.value = null
  Object.assign(formData, JSON.parse(JSON.stringify(defaultForm)))
  formData.dynamic = { port_count: 24, vlan_range: '', protocol: [], wan_count: 1, security_zone: 'trust', policy_count: 0, sub_type: 'ids', protection_level: 3, description: '' }
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.assign(formData, {
    device_name: row.device_name || '', device_type: row.device_type || 'switch',
    brand: row.brand || '', model: row.model || '', serial_number: row.serial_number || '',
    ip_address: row.ip_address || '', mac_address: row.mac_address || '',
    location: row.location || '', status: row.status || 'in_use',
    purchase_date: row.purchase_date ? row.purchase_date.split('T')[0] : '',
    warranty_expire: row.warranty_expire ? row.warranty_expire.split('T')[0] : '',
    remark: row.remark || '',
    dynamic: { port_count: 24, vlan_range: '', protocol: [], wan_count: 1, security_zone: 'trust', policy_count: 0, sub_type: 'ids', protection_level: 3, description: '' },
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  // Block submit if IP/MAC has format errors
  if (ipError.value || macError.value) {
    ElMessage.error('请修正 IP/MAC 地址格式错误')
    return
  }
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        device_name: formData.device_name, device_type: formData.device_type,
        brand: formData.brand || null, model: formData.model || null,
        serial_number: formData.serial_number || null, ip_address: formData.ip_address || null,
        mac_address: formData.mac_address || null, location: formData.location || null,
        status: formData.status, purchase_date: formData.purchase_date || null,
        warranty_expire: formData.warranty_expire || null, remark: formData.remark || null,
      }
      if (editingId.value) {
        await updateAsset(editingId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createAsset(payload)
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
  await ElMessageBox.confirm(`确定要删除设备「${row.device_name}」吗？`, '删除确认', { type: 'warning' })
  await deleteAsset(row.id)
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

/* ===== Drawer Body: Split Layout ===== */
.drawer-body {
  display: flex;
  gap: 20px;
  padding: 0 4px;
  height: 100%;
  overflow: hidden;
}
.form-panel {
  flex: 1 1 55%;
  overflow-y: auto;
  padding-right: 8px;
}
.preview-panel {
  flex: 0 0 42%;
  max-width: 420px;
  overflow-y: auto;
  position: sticky;
  top: 0;
}

/* ===== Form Section Titles ===== */
.form-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 20px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  display: flex;
  align-items: center;
  gap: 8px;
}
.form-section-title:first-child { margin-top: 0; }
.dynamic-tag { margin-left: auto; }

/* ===== Field Validation Hints ===== */
.field-hint {
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.4;
}
.field-hint.error { color: var(--el-color-danger); }
.field-hint.success { color: var(--el-color-success); }

:deep(.input-error .el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--el-color-danger) inset !important;
}
:deep(.input-valid .el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--el-color-success) inset !important;
}

/* ===== Preview Panel ===== */
.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 16px;
}

.preview-card {
  background: var(--el-bg-color-page);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-top {
  display: flex;
  align-items: center;
  gap: 14px;
}
.preview-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
  color: #fff;
}
.preview-name-area {
  flex: 1;
  min-width: 0;
}
.preview-device-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.preview-device-type {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

.preview-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.preview-info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.info-label {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  word-break: break-all;
}
.ip-valid-text { color: var(--el-color-success); }
.ip-error-text { color: var(--el-color-danger); }

.preview-dynamic {
  border-top: 1px dashed var(--el-border-color);
  padding-top: 14px;
}
.preview-dynamic-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.preview-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.preview-desc {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.preview-dates {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  border-top: 1px dashed var(--el-border-color);
  padding-top: 12px;
}

.preview-remark {
  font-size: 13px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.remark-label {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
}
.remark-text {
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.preview-completeness {
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 14px;
}
.completeness-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 6px;
}
.completeness-value {
  font-weight: 700;
  font-size: 14px;
}
</style>
