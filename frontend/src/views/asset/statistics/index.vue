<template>
  <div class="page-container">
    <!-- Search card (standalone, separated from the content table) -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="设备名称/IP/序列号" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-cascader
            v-model="searchForm.device_type"
            :options="deviceTypes"
            placeholder="全部"
            clearable
            style="width: 200px"
            :props="{ expandTrigger: 'hover', emitPath: false, value: 'value', label: 'label', children: 'options' }"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="组织">
          <el-select v-model="searchForm.organization" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="item in organizationOptions" :key="item.value" :label="item.label" :value="item.value" />
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

    <!-- Table + Quick Preview Split Layout -->
    <div class="main-split">
      <!-- Left: Table -->
      <el-card shadow="never" class="table-card" :class="{ 'with-preview': selectedRow }">
        <div class="table-header">
          <span class="table-title">设备列表</span>
          <div class="table-header-actions">
            <el-popover placement="bottom-end" :width="180" trigger="click">
              <template #reference>
                <el-button text>
                  <el-icon><Operation /></el-icon> 列设置
                </el-button>
              </template>
              <div class="col-settings">
                <div class="col-settings-header">
                  <span>显示列</span>
                  <el-button text size="small" type="primary" @click="resetColumns">重置</el-button>
                </div>
                <div class="col-settings-list">
                  <el-checkbox
                    v-for="col in allTableColumns"
                    :key="col.prop"
                    :model-value="isColumnVisible(col.prop)"
                    @change="toggleColumn(col.prop)"
                  >
                    {{ col.label }}
                  </el-checkbox>
                </div>
              </div>
            </el-popover>
            <el-tag v-if="selectedRow" size="small" type="info" effect="plain">
              已选中: {{ selectedRow.device_name }}
            </el-tag>
            <el-tooltip v-if="userStore.isAdmin" content="在表单设计器中编辑此表单字段" placement="top">
              <el-button @click="goToDesigner">
                <el-icon><Setting /></el-icon> 编辑表单
              </el-button>
            </el-tooltip>
            <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增设备
            </el-button>
          </div>
        </div>
        <div class="table-area" ref="tableAreaRef">
        <el-table
          :data="tableData"
          v-loading="loading"
          border
          stripe
          highlight-current-row
          style="width: 100%"
          :height="tableHeight"
          :default-sort="{ prop: 'id', order: 'ascending' }"
          @sort-change="handleSortChange"
          @row-click="handleRowClick"
          @row-dblclick="handleDetail"
        >
          <IdColumn :visible="isColumnVisible('id')" />
          <el-table-column v-if="isColumnVisible('organization')" label="组织" :min-width="colWidth('organization')" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ resolveOptionLabel(organizationOptions, row.organization) }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('device_name')" prop="device_name" label="设备名称" :min-width="colWidth('device_name')">
            <template #default="{ row }">
              <div class="device-name-cell">
                <DeviceTypeIcon :val="row.device_type" size="small" />
                <span>{{ row.device_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('device_type')" prop="device_type" label="类型" :min-width="colWidth('device_type')">
            <template #default="{ row }">
              <el-tag :color="deviceTypeColor(row.device_type)" effect="dark" size="small" round>
                {{ deviceTypeLabel(row.device_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('brand')" prop="brand" label="品牌" :min-width="colWidth('brand')" show-overflow-tooltip />
          <el-table-column v-if="isColumnVisible('model')" prop="model" label="型号" :min-width="colWidth('model')" show-overflow-tooltip />
          <el-table-column v-if="isColumnVisible('ip_address')" prop="ip_address" label="管理IP" :min-width="colWidth('ip_address')" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.ip_address" class="ip-text">{{ row.ip_address }}</span>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('mac_address')" prop="mac_address" label="MAC地址" :min-width="colWidth('mac_address')" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.mac_address" class="mono-text">{{ row.mac_address }}</span>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('serial_number')" prop="serial_number" label="序列号" :min-width="colWidth('serial_number')" show-overflow-tooltip />
          <el-table-column v-if="isColumnVisible('it_asset_code')" prop="it_asset_code" label="IT资产编码" :min-width="colWidth('it_asset_code')" show-overflow-tooltip />
          <el-table-column v-if="isColumnVisible('financial_asset_code')" prop="financial_asset_code" label="财务资产编码" :min-width="colWidth('financial_asset_code')" show-overflow-tooltip />
          <el-table-column v-if="isColumnVisible('location')" label="位置" :min-width="colWidth('location')" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ resolveOptionLabel(locationOptions, row.location) }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('cabinet_u')" prop="cabinet_u" label="机柜U位" :min-width="colWidth('cabinet_u')" show-overflow-tooltip />
          <!-- Dynamic columns for custom fields from form designer -->
          <el-table-column
            v-for="field in visibleDynamicFields"
            :key="field.prop"
            :label="field.label"
            :min-width="colWidth(field.prop, 140)"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span>{{ formatFieldValue(row, field) }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('status')" prop="status" label="状态" :min-width="colWidth('status')">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('purchase_date')" prop="purchase_date" label="采购日期" :min-width="colWidth('purchase_date')">
            <template #default="{ row }">
              <span class="text-muted">{{ formatDate(row.purchase_date) }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('warranty_expire')" prop="warranty_expire" label="保修到期" :min-width="colWidth('warranty_expire')">
            <template #default="{ row }">
              <span class="text-muted">{{ formatDate(row.warranty_expire) }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('remark')" prop="remark" label="备注" :min-width="colWidth('remark')" show-overflow-tooltip />
          <el-table-column v-if="isColumnVisible('created_at')" prop="created_at" label="创建时间" :min-width="colWidth('created_at')">
            <template #default="{ row }">
              <span class="text-muted">{{ formatDateTime(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" :min-width="colWidth('operation')" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" link @click.stop="handleDetail(row)">
                <el-icon><View /></el-icon> 查看
              </el-button>
              <el-button size="small" link @click.stop="handleEdit(row)">编辑</el-button>
              <el-button v-if="userStore.isAdmin" size="small" type="danger" link @click.stop="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        </div>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 15, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          class="pagination"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </el-card>

      <!-- Right: Quick Preview Panel (shows when a row is selected) -->
      <transition name="slide-preview">
        <el-card v-if="selectedRow" shadow="never" class="quick-preview-card">
          <template #header>
            <div class="quick-preview-header">
              <span><el-icon><View /></el-icon> 快速预览</span>
              <el-button text size="small" @click="selectedRow = null">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="quick-preview-body">
            <div class="qp-top">
              <DeviceTypeIcon :val="selectedRow.device_type" size="medium" />
              <div class="qp-name-area">
                <div class="qp-name">{{ selectedRow.device_name }}</div>
                <div class="qp-type">{{ deviceTypeLabel(selectedRow.device_type) }} · {{ selectedRow.brand || '未知品牌' }}</div>
              </div>
              <el-tag :type="statusTagType(selectedRow.status)" effect="dark" size="small">
                {{ statusLabel(selectedRow.status) }}
              </el-tag>
            </div>
            <div class="qp-info-grid">
              <div class="qp-info-item" v-for="field in previewFields" :key="field.prop">
                <span class="qp-label">{{ field.label }}</span>
                <span class="qp-value">{{ formatFieldValue(selectedRow, field) }}</span>
              </div>
            </div>
            <div class="qp-dates" v-if="selectedRow.purchase_date || selectedRow.warranty_expire">
              <div v-if="selectedRow.purchase_date">
                <el-icon><Calendar /></el-icon> 采购: {{ formatDate(selectedRow.purchase_date) }}
              </div>
              <div v-if="selectedRow.warranty_expire">
                <el-icon><Timer /></el-icon> 保修至: {{ formatDate(selectedRow.warranty_expire) }}
              </div>
            </div>
            <div class="qp-remark" v-if="selectedRow.remark">
              <span class="qp-remark-label">备注</span>
              <span class="qp-remark-text">{{ selectedRow.remark }}</span>
            </div>
            <div class="qp-actions">
              <el-button type="primary" size="small" @click="handleDetail(selectedRow)">查看详情</el-button>
              <el-button v-if="userStore.isAdmin" size="small" @click="handleEdit(selectedRow)">编辑</el-button>
            </div>
            <div class="qp-hint">
              <el-icon><InfoFilled /></el-icon> 双击表格行可快速打开详情
            </div>
          </div>
        </el-card>
      </transition>
    </div>

    <!-- ==================== Detail Drawer (Read-Only) ==================== -->
    <el-drawer v-model="detailVisible" title="设备详情" size="55%" :close-on-click-modal="true">
      <div v-if="detailData" class="detail-body">
        <div class="detail-hero">
          <DeviceTypeIcon :val="detailData.device_type" size="large" />
          <div class="detail-hero-info">
            <div class="detail-hero-name">{{ detailData.device_name }}</div>
            <div class="detail-hero-meta">
              <el-tag :color="deviceTypeColor(detailData.device_type)" effect="dark" size="small" round>
                {{ deviceTypeLabel(detailData.device_type) }}
              </el-tag>
              <span class="detail-hero-brand">{{ detailData.brand || '未知品牌' }} · {{ detailData.model || '型号未知' }}</span>
            </div>
          </div>
          <el-tag :type="statusTagType(detailData.status)" effect="dark" size="large">
            {{ statusLabel(detailData.status) }}
          </el-tag>
        </div>
        <el-descriptions :column="2" border class="detail-desc">
          <el-descriptions-item
            v-for="field in detailFields"
            :key="field.prop"
            :label="field.label"
          >{{ formatFieldValue(detailData, field) }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="detailData.remark" class="detail-remark-section">
          <div class="detail-section-title"><el-icon><ChatLineSquare /></el-icon> 备注</div>
          <div class="detail-remark-box">{{ detailData.remark }}</div>
        </div>
        <div v-if="detailData.extra_data?.stack_config?.enabled && (detailData.extra_data?.stack_config?.members || []).length" class="detail-remark-section">
          <div class="detail-section-title"><el-icon><Connection /></el-icon> 堆叠成员 ({{ detailData.extra_data.stack_config.members.length }} 台)</div>
          <el-table :data="detailData.extra_data.stack_config.members" border size="small">
            <el-table-column type="index" label="#" :min-width="colWidth('index')" />
            <el-table-column prop="name" label="设备名称" :min-width="colWidth('device_name')" />
            <el-table-column prop="serial_number" label="序列号" :min-width="colWidth('serial_number')" />
            <el-table-column prop="it_asset_code" label="IT资产编码" :min-width="colWidth('it_asset_code')" />
            <el-table-column prop="financial_asset_code" label="财务资产编码" :min-width="colWidth('financial_asset_code')" />
          </el-table>
        </div>
        <div class="detail-actions">
          <el-button v-if="userStore.isAdmin" type="primary" @click="handleEditFromDetail">
            <el-icon><Edit /></el-icon> 编辑此设备
          </el-button>
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- ==================== Add/Edit Drawer with Schema-Driven Form + Live Preview ==================== -->
    <el-drawer
      v-model="dialogVisible"
      :title="editingId ? '编辑设备' : '新增设备'"
      size="75%"
      :close-on-click-modal="false"
    >
      <div class="drawer-body">
        <!-- ===== Left: Schema-Driven Form ===== -->
        <div class="form-panel">
          <div v-if="schemaLoading" class="schema-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载表单配置中...</span>
          </div>
          <SchemaFormRenderer
            v-else
            ref="schemaFormRef"
            :fields="formSchema"
            :modelValue="formData"
            @update:modelValue="onFormUpdate"
          />
          <!-- Form source indicator -->
          <div class="form-source-info">
            <el-tag size="small" :type="schemaSource === 'backend' ? 'success' : 'info'" effect="plain">
              {{ schemaSource === 'backend' ? '表单来源: 数据库配置' : '表单来源: 默认模板' }}
            </el-tag>
            <el-button v-if="userStore.isAdmin" text size="small" type="primary" @click="goToDesigner">
              <el-icon><Setting /></el-icon> 去设计器修改
            </el-button>
          </div>
        </div>

        <!-- ===== Right: Live Preview ===== -->
        <div class="preview-panel">
          <div class="preview-header">
            <el-icon><View /></el-icon>
            <span>实时预览</span>
            <el-tag size="small" type="success" effect="dark">LIVE</el-tag>
          </div>
          <div class="preview-card">
            <!-- Device header -->
            <div class="preview-top">
              <DeviceTypeIcon :val="formData.device_type" size="medium" />
              <div class="preview-name-area">
                <div class="preview-device-name">{{ formData.device_name || '未命名设备' }}</div>
                <div class="preview-device-type">
                  {{ deviceTypeLabel(formData.device_type) }} · {{ formData.brand || '未知品牌' }}
                </div>
              </div>
              <el-tag :type="statusTagType(formData.status)" effect="dark" size="small">
                {{ statusLabel(formData.status) }}
              </el-tag>
            </div>

            <!-- Schema-driven info grid -->
            <div class="preview-info-grid">
              <div
                v-for="field in previewSchemaFields"
                :key="field.prop"
                class="preview-info-item"
              >
                <span class="info-label">{{ field.label }}</span>
                <span class="info-value">{{ formatPreviewValue(field) }}</span>
              </div>
            </div>

            <!-- Dates -->
            <div class="preview-dates" v-if="formData.purchase_date || formData.warranty_expire">
              <div v-if="formData.purchase_date">采购: {{ formData.purchase_date }}</div>
              <div v-if="formData.warranty_expire">保修至: {{ formData.warranty_expire }}</div>
            </div>

            <!-- Remark -->
            <div class="preview-remark" v-if="formData.remark">
              <span class="remark-label">备注</span>
              <span class="remark-text">{{ formData.remark }}</span>
            </div>

            <!-- Completeness -->
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTableHeight } from '@/composables/useTableHeight'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, View, Close, Calendar, Timer, InfoFilled,
  Edit, ChatLineSquare, Setting, Loading, Operation, Connection,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getAssets, getAsset, createAsset, updateAsset, deleteAsset } from '@/api/asset'
import { getFormConfigByCode } from '@/api/form_config'
import { defaultAssetFormSchema, coreAssetFields } from '@/api/assetFormSchema'
import SchemaFormRenderer from '@/components/SchemaFormRenderer.vue'
import DeviceTypeIcon from '@/components/DeviceTypeIcon.vue'
import { buildDeviceTypeIconMap } from '@/composables/deviceTypeIcons'
import { summarizePortGroups } from '@/utils/portNaming'
import { DEVICE_CATEGORY_TREE, DEVICE_TYPE_LABEL_MAP, getDeviceTypeIcon, deviceTypeLabel as deviceTypeLabelFn } from '@/constants/vendors'
import { resolveSystemFieldOptions, getFieldOptions, buildDeviceTypeLabelMap } from '@/api/system-field'
import IdColumn from '@/components/IdColumn.vue'
import { colWidth } from '@/constants/columnWidths'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const schemaFormRef = ref()

// ===== Schema state (drives dynamic columns + detail/preview + edit form) =====
const formSchema = ref(defaultAssetFormSchema)
const schemaLoading = ref(false)
const schemaSource = ref('default') // 'backend' or 'default'

// ===== Detail drawer state =====
const detailVisible = ref(false)
const detailData = ref(null)

// ===== Quick preview state =====
const selectedRow = ref(null)

// ===== Add/Edit form state =====
const formData = reactive({})
function onFormUpdate(val) {
  Object.keys(val).forEach((key) => {
    formData[key] = val[key]
  })
}

const deviceTypes = ref(DEVICE_CATEGORY_TREE)
const dynamicDeviceTypeLabelMap = ref({})
const organizationOptions = ref([])
const locationOptions = ref([])

const statusOptions = [
  { label: '使用中', value: 'in_use' },
  { label: '空闲', value: 'idle' },
  { label: '故障', value: 'fault' },
  { label: '维护中', value: 'maintenance' },
  { label: '已报废', value: 'scrap' },
]

const searchForm = reactive({ keyword: '', device_type: '', status: '', organization: '' })
const pagination = reactive({ page: 1, size: 15, total: 0 })

// 表格区域高度（填满视口，表格内部滚动，整页不下拉）
const tableAreaRef = ref(null)
const { tableHeight } = useTableHeight(tableAreaRef)

// ID 排序：desc(倒序，默认) / asc(正序)
const sortState = ref('asc')

// ===== Load schema from backend (drives dynamic columns + detail/preview + edit form) =====
async function loadFormSchema() {
  schemaLoading.value = true
  try {
    const config = await getFormConfigByCode('asset_form')
    if (config && config.form_schema) {
      const parsed = typeof config.form_schema === 'string'
        ? JSON.parse(config.form_schema)
        : config.form_schema
      if (Array.isArray(parsed) && parsed.length > 0) {
        formSchema.value = await resolveSystemFieldOptions(parsed)
        schemaSource.value = 'backend'
        // 将字段管理中为 device_type 选项配置的图标注入全局覆盖表，
        // 使统计页/端口互联页的 <DeviceTypeIcon> 优先显示已上传的图标。
        const dt = formSchema.value.find((f) => f.prop === 'device_type')
        const dtOpts = dt ? (dt.cascaderOptions || dt.options) : null
        if (dtOpts && dtOpts.length) buildDeviceTypeIconMap(dtOpts)
      }
    }
  } catch {
    // 404 or other error — use default schema
    schemaSource.value = 'default'
  } finally {
    schemaLoading.value = false
  }
}

// ==================== Computed: fields for preview/detail (non-layout, non-dynamic) ====================

// Dynamic table columns: non-core, non-layout fields from schema
const dynamicTableFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    if (coreAssetFields.includes(f.prop)) return false
    if (['id', 'created_at', 'updated_at'].includes(f.prop)) return false
    return true
  })
})

// ===== Column visibility settings =====
const COLUMN_STORAGE_KEY = 'asset_table_visible_columns'

// Core table columns (static, always in selector)
const coreTableColumns = [
  { prop: 'id', label: 'ID' },
  { prop: 'organization', label: '组织' },
  { prop: 'device_name', label: '设备名称' },
  { prop: 'device_type', label: '类型' },
  { prop: 'brand', label: '品牌' },
  { prop: 'model', label: '型号' },
  { prop: 'ip_address', label: '管理IP' },
  { prop: 'mac_address', label: 'MAC地址' },
  { prop: 'serial_number', label: '序列号' },
  { prop: 'it_asset_code', label: 'IT资产编码' },
  { prop: 'financial_asset_code', label: '财务资产编码' },
  { prop: 'location', label: '位置' },
  { prop: 'cabinet_u', label: '机柜U位' },
  { prop: 'status', label: '状态' },
  { prop: 'purchase_date', label: '采购日期' },
  { prop: 'warranty_expire', label: '保修到期' },
  { prop: 'remark', label: '备注' },
  { prop: 'created_at', label: '创建时间' },
]

// Default visible column props
const defaultVisibleColumns = [
  'id', 'organization', 'device_name', 'device_type', 'brand', 'model',
  'ip_address', 'vlan_range', 'location', 'cabinet_u', 'status',
]

// Visible column keys (persisted in localStorage)
const visibleColumnKeys = ref([])

function initColumnVisibility() {
  try {
    const saved = localStorage.getItem(COLUMN_STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length > 0) {
        visibleColumnKeys.value = parsed
        return
      }
    }
  } catch {}
  visibleColumnKeys.value = [...defaultVisibleColumns]
}

watch(visibleColumnKeys, (val) => {
  try {
    localStorage.setItem(COLUMN_STORAGE_KEY, JSON.stringify(val))
  } catch {}
}, { deep: true })

function isColumnVisible(prop) {
  return visibleColumnKeys.value.includes(prop)
}

function toggleColumn(prop) {
  const idx = visibleColumnKeys.value.indexOf(prop)
  if (idx >= 0) {
    visibleColumnKeys.value.splice(idx, 1)
  } else {
    visibleColumnKeys.value.push(prop)
  }
}

function resetColumns() {
  visibleColumnKeys.value = [...defaultVisibleColumns]
}

// All selectable columns (core + dynamic from schema)
const allTableColumns = computed(() => {
  return [
    ...coreTableColumns,
    ...dynamicTableFields.value.map(f => ({ prop: f.prop, label: f.label, dynamic: true })),
  ]
})

// Visible dynamic fields (filtered by visibility setting)
const visibleDynamicFields = computed(() => {
  return dynamicTableFields.value.filter(f => visibleColumnKeys.value.includes(f.prop))
})

const previewSchemaFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    if (['device_name', 'device_type', 'brand', 'status', 'remark', 'purchase_date', 'warranty_expire'].includes(f.prop)) return false
    // Check visibility condition
    if (f.visibleWhen) {
      const val = formData[f.visibleWhen.prop]
      if (f.visibleWhen.equals !== undefined && val !== f.visibleWhen.equals) return false
      if (f.visibleWhen.in !== undefined && !f.visibleWhen.in.includes(val)) return false
    }
    return true
  })
})

function isFieldVisibleForRow(field, row) {
  if (!field.visibleWhen || !row) return true
  const cond = field.visibleWhen
  const val = row[cond.prop]
  if (cond.equals !== undefined) return val === cond.equals
  if (cond.in !== undefined) return cond.in.includes(val)
  if (cond.notEquals !== undefined) return val !== cond.notEquals
  return true
}

const previewFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    // device_type 不再被排除：让设备类型与"组织"在 preview 字段列表并排出现（走 select-cascade 解析 → 中文 label）
    if (['device_name', 'brand', 'status', 'remark', 'purchase_date', 'warranty_expire', 'created_at', 'updated_at'].includes(f.prop)) return false
    return isFieldVisibleForRow(f, selectedRow.value)
  })
})

const detailFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    return isFieldVisibleForRow(f, detailData.value)
  })
})

// ==================== Completeness Score ====================
const completeness = computed(() => {
  const dataFields = formSchema.value.filter((f) => !['divider', 'alert', 'text'].includes(f.type))
  if (dataFields.length === 0) return 0
  let filled = 0
  dataFields.forEach((f) => {
    const val = formData[f.prop]
    if (val !== undefined && val !== '' && val !== null && !(Array.isArray(val) && val.length === 0)) {
      filled++
    }
  })
  return Math.round((filled / dataFields.length) * 100)
})
const completenessColor = computed(() => {
  if (completeness.value >= 80) return '#67c23a'
  if (completeness.value >= 50) return '#e6a23c'
  return '#f56c6c'
})

// ==================== Helpers ====================
function deviceTypeLabel(val) {
  if (!val) return '未分类'
  return dynamicDeviceTypeLabelMap.value[val] || deviceTypeLabelFn(val)
}
function statusLabel(val) {
  return statusOptions.find((s) => s.value === val)?.label || val
}
function statusTagType(val) {
  const map = { in_use: 'success', idle: 'info', fault: 'danger', maintenance: 'warning', scrap: '' }
  return map[val] || ''
}

// ==================== 设备类型按大类配色（网络=蓝 / 安全=红 / 软件=紫） ====================
// 从 DEVICE_CATEGORY_TREE 自动派生出 value → 类别索引，避免硬编码漏改。
const DEVICE_CATEGORY_COLORS = ['#409EFF', '#F56C6C', '#722ED1'] // 蓝 / 红 / 紫（Element Plus primary / danger / 自定义紫）
const DEVICE_TYPE_CATEGORY_INDEX = (() => {
  const m = {}
  DEVICE_CATEGORY_TREE.forEach((cat, idx) => {
    ;(cat.options || []).forEach((o) => { m[o.value] = idx })
  })
  return m
})()

// 主题色优先取自 vendors.js 的 themeColor（保持单一真源），
// 兜底从 DEVICE_CATEGORY_COLORS 取（向后兼容）。
function deviceTypeColor(val) {
  const iconInfo = getDeviceTypeIcon(val)
  if (iconInfo.themeColor) return iconInfo.themeColor
  const idx = DEVICE_TYPE_CATEGORY_INDEX[val]
  return idx === undefined ? '#909399' : DEVICE_CATEGORY_COLORS[idx]
}
function formatDateTime(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
function formatDate(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// ==================== Format field value for preview/detail ====================
function formatFieldValue(row, field) {
  // Try row[prop] first (core field), then extra_data[prop] (custom field from designer)
  let val = row[field.prop]
  if (val === undefined || val === null) {
    val = row.extra_data?.[field.prop]
  }
  // Custom structured fields: port groups / stacking config
  if (field.prop === 'port_groups') return summarizePortGroups(val)
  if (field.prop === 'stack_config') {
    if (!val || !val.enabled) return '未开启堆叠'
    return `堆叠: 开启 (${Number(val.count) || 0} 台)`
  }
  if (val === undefined || val === null || val === '') return '—'
  // Cascader / select-cascade: cascaderOptions = [{label, options:[{value,label}]}, ...]
  if ((field.type === 'cascader' || field.type === 'select-cascade') && Array.isArray(field.cascaderOptions)) {
    for (const cat of field.cascaderOptions) {
      for (const opt of cat.options || []) {
        if (opt.value === val) return opt.label || val
      }
    }
    return val // not found, fallback to raw value
  }
  if (field.type === 'select' && field.options) {
    if (Array.isArray(val)) {
      if (val.length === 0) return '—'
      return val.map((v) => field.options.find((o) => o.value === v)?.label || v).join(', ')
    }
    const opt = field.options.find((o) => o.value === val)
    return opt ? opt.label : val
  }
  if (field.type === 'date') return formatDate(val)
  if (field.type === 'datetime') return formatDateTime(val)
  if (Array.isArray(val)) {
    if (val.length === 0) return '—'
    return val.join(', ')
  }
  return val
}

// Resolve a stored value to its option label, for system_field-sourced columns
// (e.g. organization/location: DB stores value=internal code, label=display name).
// Falls back to the raw value when the option cannot be found.
function resolveOptionLabel(options, value) {
  if (value === undefined || value === null || value === '') return '—'
  const opt = (options || []).find((o) => o.value === value)
  return opt ? opt.label : value
}

function formatPreviewValue(field) {
  return formatFieldValue(formData, field)
}

// ==================== Go to Form Designer ====================
function goToDesigner() {
  router.push('/system/designer')
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
      organization: searchForm.organization || undefined,
      order: sortState.value,
    })
    tableData.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

// ID 列排序切换：默认倒序，点击切换 asc/desc
function handleSortChange({ prop, order }) {
  if (prop !== 'id') return
  sortState.value = sortState.value === 'desc' ? 'asc' : 'desc'
  fetchData()
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.device_type = ''
  searchForm.status = ''
  searchForm.organization = ''
  handleSearch()
}

// ==================== Row Click → Quick Preview ====================
function handleRowClick(row) {
  selectedRow.value = row
}

// ==================== Double Click / View Button → Detail Drawer ====================
async function handleDetail(row) {
  try {
    const data = await getAsset(row.id)
    detailData.value = data
  } catch {
    detailData.value = row
  }
  detailVisible.value = true
}

// ==================== Edit from Detail Drawer ====================
function handleEditFromDetail() {
  if (!detailData.value) return
  detailVisible.value = false
  handleEdit(detailData.value)
}

function handleAdd() {
  editingId.value = null
  // Clear form data — SchemaFormRenderer will initialize defaults
  Object.keys(formData).forEach((k) => delete formData[k])
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  // Clear and populate form data from row
  Object.keys(formData).forEach((k) => delete formData[k])
  // Merge extra_data into a flat lookup so schema fields can find their values
  const extra = row.extra_data || {}
  // Map all schema fields from row data (core fields + extra_data)
  formSchema.value.forEach((field) => {
    if (['divider', 'alert', 'text'].includes(field.type)) return
    // Try row[prop] first (core field), then extra_data[prop] (custom field)
    let val = row[field.prop]
    if (val === undefined || val === null) {
      val = extra[field.prop]
    }
    if (val !== undefined && val !== null) {
      if (field.type === 'date' && typeof val === 'string') {
        formData[field.prop] = val.split('T')[0]
      } else {
        formData[field.prop] = val
      }
    }
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!schemaFormRef.value) return
  try {
    await schemaFormRef.value.validate()
  } catch {
    ElMessage.warning('请完善必填项')
    return
  }
  submitting.value = true
  try {
    // Core fields → top-level; custom fields → extra_data
    const payload = {}
    const extraData = {}
    // Default values for required str fields (prevents 422 when field is empty)
    const fieldDefaults = { device_type: 'other', status: 'in_use' }
    formSchema.value.forEach((field) => {
      if (['divider', 'alert', 'text'].includes(field.type)) return
      // Skip conditional fields that are currently hidden (e.g. port/stack config on non-switch)
      if (field.visibleWhen && !isFieldVisibleForRow(field, formData)) return
      const val = formData[field.prop]
      if (coreAssetFields.includes(field.prop)) {
        if (val !== undefined && val !== '' && val !== null) {
          payload[field.prop] = val
        } else if (fieldDefaults[field.prop]) {
          payload[field.prop] = fieldDefaults[field.prop]
        } else {
          payload[field.prop] = null
        }
      } else {
        if (val !== undefined && val !== '' && val !== null) {
          extraData[field.prop] = val
        }
      }
    })
    payload.extra_data = Object.keys(extraData).length > 0 ? extraData : null

    if (editingId.value) {
      await updateAsset(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createAsset(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    const detail = err?.response?.data?.detail
    const message = typeof detail === 'string'
      ? detail
      : (err?.message || '未知错误')
    ElMessage.error('操作失败: ' + message)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定要删除设备「${row.device_name}」吗？`, '删除确认', { type: 'warning' })
  await deleteAsset(row.id)
  ElMessage.success('删除成功')
  if (selectedRow.value?.id === row.id) selectedRow.value = null
  fetchData()
}

onMounted(() => {
  initColumnVisibility()
  loadDeviceTypeOptions()
  loadOrganizationOptions()
  loadLocationOptions()
  loadFormSchema()
  fetchData()
})

async function loadDeviceTypeOptions() {
  const tree = await getFieldOptions('device_type')
  if (Array.isArray(tree) && tree.length) {
    deviceTypes.value = tree
    dynamicDeviceTypeLabelMap.value = buildDeviceTypeLabelMap(tree)
  }
}

async function loadOrganizationOptions() {
  organizationOptions.value = await getFieldOptions('organization')
}

async function loadLocationOptions() {
  locationOptions.value = await getFieldOptions('location')
}
</script>

<style scoped>

/* ===== Main Split Layout ===== */

/* ===== Table Header ===== */

/* ===== Table Cell Styles ===== */
.device-name-cell { display: flex; align-items: center; gap: 8px; }
.ip-text { font-family: 'Courier New', monospace; font-weight: 500; color: var(--el-color-primary); }
.mono-text { font-family: 'Courier New', monospace; font-size: 13px; }

/* ===== Quick Preview Panel ===== */
.quick-preview-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }
.quick-preview-header span { display: flex; align-items: center; gap: 6px; }
.quick-preview-body { display: flex; flex-direction: column; gap: 16px; }
.qp-top { display: flex; align-items: center; gap: 12px; }
.qp-name-area { flex: 1; min-width: 0; }
.qp-name { font-size: 16px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.qp-type { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 2px; }
.qp-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qp-info-item { display: flex; flex-direction: column; gap: 2px; }
.qp-label { font-size: 11px; color: var(--el-text-color-secondary); text-transform: uppercase; letter-spacing: 0.3px; }
.qp-value { font-size: 13px; font-weight: 500; word-break: break-all; }
.qp-dates { display: flex; flex-direction: column; gap: 6px; font-size: 12px; color: var(--el-text-color-secondary); border-top: 1px dashed var(--el-border-color); padding-top: 10px; }
.qp-dates div { display: flex; align-items: center; gap: 4px; }
.qp-remark { background: var(--el-fill-color-light); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; }
.qp-remark-label { font-size: 11px; color: var(--el-text-color-secondary); text-transform: uppercase; }
.qp-remark-text { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.5; }
.qp-actions { display: flex; gap: 8px; }
.qp-hint { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--el-text-color-placeholder); margin-top: 4px; }

.slide-preview-enter-active, .slide-preview-leave-active { transition: all 0.3s ease; }
.slide-preview-enter-from, .slide-preview-leave-to { opacity: 0; transform: translateX(20px); }

/* ===== Detail Drawer ===== */
.detail-body { padding: 0 4px; display: flex; flex-direction: column; gap: 20px; }
.detail-hero { display: flex; align-items: center; gap: 16px; background: var(--el-bg-color-page); border-radius: 12px; padding: 20px; }
.detail-hero-info { flex: 1; min-width: 0; }
.detail-hero-name { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.detail-hero-meta { display: flex; align-items: center; gap: 8px; }
.detail-hero-brand { font-size: 13px; color: var(--el-text-color-secondary); }
.detail-desc { margin-top: 4px; }
.detail-section-title { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; margin-bottom: 10px; color: var(--el-text-color-primary); }
.detail-remark-box { background: var(--el-fill-color-light); border-radius: 8px; padding: 14px 16px; font-size: 14px; line-height: 1.6; color: var(--el-text-color-regular); }
.detail-actions { display: flex; gap: 10px; padding-top: 8px; }

/* ===== Drawer Body: Split Layout ===== */
.drawer-body { display: flex; gap: 20px; padding: 0 4px; height: 100%; overflow: hidden; }
.form-panel { flex: 1 1 55%; overflow-y: auto; padding-right: 8px; }
.preview-panel { flex: 0 0 42%; max-width: 420px; overflow-y: auto; position: sticky; top: 0; }

/* ===== Schema Loading ===== */
.schema-loading { display: flex; align-items: center; gap: 8px; justify-content: center; padding: 60px 0; color: var(--el-text-color-secondary); font-size: 14px; }
.schema-loading .is-loading { font-size: 20px; }

/* ===== Form Source Info ===== */
.form-source-info { display: flex; align-items: center; gap: 8px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--el-border-color-lighter); }

/* ===== Preview Panel ===== */
.preview-header { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: var(--el-text-color-primary); margin-bottom: 16px; }
.preview-card { background: var(--el-bg-color-page); border: 1px solid var(--el-border-color-lighter); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.preview-top { display: flex; align-items: center; gap: 14px; }
.preview-name-area { flex: 1; min-width: 0; }
.preview-device-name { font-size: 18px; font-weight: 700; color: var(--el-text-color-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.preview-device-type { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }
.preview-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.preview-info-item { display: flex; flex-direction: column; gap: 2px; }
.info-label { font-size: 11px; color: var(--el-text-color-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.info-value { font-size: 14px; font-weight: 500; color: var(--el-text-color-primary); word-break: break-all; }
.preview-dates { display: flex; gap: 16px; font-size: 12px; color: var(--el-text-color-secondary); border-top: 1px dashed var(--el-border-color); padding-top: 12px; }
.preview-remark { font-size: 13px; background: var(--el-fill-color-light); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; }
.remark-label { font-size: 11px; color: var(--el-text-color-secondary); text-transform: uppercase; }
.remark-text { color: var(--el-text-color-regular); line-height: 1.5; }
.preview-completeness { border-top: 1px solid var(--el-border-color-lighter); padding-top: 14px; }
.completeness-label { display: flex; justify-content: space-between; font-size: 12px; color: var(--el-text-color-secondary); margin-bottom: 6px; }
.completeness-value { font-weight: 700; font-size: 14px; }

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

/* ===== Column Settings Popover ===== */
</style>
