<template>
  <div class="crud-page-container">
    <!-- Search bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchKeyword" :placeholder="searchPlaceholder" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <slot name="search-filters" :searchForm="searchForm" />
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table + Quick Preview -->
    <div class="main-split">
      <el-card shadow="never" class="table-card" :class="{ 'with-preview': selectedRow }">
        <div class="table-header">
          <span class="table-title">{{ title }}</span>
          <div class="table-header-actions">
            <el-popover placement="bottom-end" :width="200" trigger="click">
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
                  >{{ col.label }}</el-checkbox>
                </div>
              </div>
            </el-popover>
            <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
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
          :default-sort="{ prop: 'id', order: 'descending' }"
          @sort-change="handleSortChange"
          @row-click="handleRowClick"
          @row-dblclick="handleDetail"
        >
          <el-table-column v-if="isColumnVisible('id')" prop="id" label="ID" width="70" sortable="custom" />
          <!-- Core columns from props -->
          <el-table-column
            v-for="col in visibleCoreColumns"
            :key="col.prop"
            :prop="col.prop"
            :label="col.label"
            :width="col.width"
            :min-width="col.minWidth || 120"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span v-if="col.type === 'tag'" class="cell-tag-wrap">
                <el-tag
                  v-if="getTagColor(col, row)"
                  :color="getTagColor(col, row)"
                  size="small"
                  effect="dark"
                  style="border: none; color: #fff"
                >{{ getTagLabel(col, row) }}</el-tag>
                <el-tag v-else :type="getTagType(col, row)" size="small">{{ getTagLabel(col, row) }}</el-tag>
              </span>
              <span v-else-if="col.type === 'icon'" class="cell-icon-wrap">
                <img v-if="getIconSrc(col, row)" :src="getIconSrc(col, row)" class="cell-icon" alt="" />
                <span v-else-if="getEmoji(col, row)" class="cell-emoji">{{ getEmoji(col, row) }}</span>
                <span>{{ getTagLabel(col, row) }}</span>
              </span>
              <span v-else-if="col.type === 'date'">{{ formatDate(getCellValue(row, col.prop)) }}</span>
              <span v-else-if="col.type === 'datetime'">{{ formatDateTime(getCellValue(row, col.prop)) }}</span>
              <span v-else>{{ getCellValue(row, col.prop) || '—' }}</span>
            </template>
          </el-table-column>
          <!-- Dynamic columns from schema (non-core fields) -->
          <el-table-column
            v-for="field in visibleDynamicFields"
            :key="field.prop"
            :label="field.label"
            :min-width="120"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span>{{ formatFieldValue(row, field) }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('created_at')" prop="created_at" label="创建时间" width="160">
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

      <!-- Quick Preview -->
      <transition name="slide-preview">
        <el-card v-if="selectedRow" shadow="never" class="quick-preview-card">
          <template #header>
            <div class="qp-header">
              <span><el-icon><View /></el-icon> 快速预览</span>
              <el-button text size="small" @click="selectedRow = null"><el-icon><Close /></el-icon></el-button>
            </div>
          </template>
          <div class="qp-body">
            <div class="qp-name">{{ getCellValue(selectedRow, nameField) || '未命名' }}</div>
            <div class="qp-info-grid">
              <div class="qp-info-item" v-for="field in previewFields" :key="field.prop">
                <span class="qp-label">{{ field.label }}</span>
                <span class="qp-value">
                  <img v-if="getSelectIcon(field, selectedRow)" :src="getSelectIcon(field, selectedRow)" class="cell-icon" alt="" />
                  <span v-else-if="getSelectEmoji(field, selectedRow)" class="cell-emoji">{{ getSelectEmoji(field, selectedRow) }}</span>
                  {{ formatFieldValue(selectedRow, field) }}
                </span>
              </div>
            </div>
            <div class="qp-actions">
              <el-button type="primary" size="small" @click="handleDetail(selectedRow)">查看详情</el-button>
              <el-button v-if="userStore.isAdmin" size="small" @click="handleEdit(selectedRow)">编辑</el-button>
            </div>
            <div class="qp-hint">双击表格行可快速打开详情</div>
          </div>
        </el-card>
      </transition>
    </div>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" :title="title + '详情'" size="55%">
      <div v-if="detailData" class="detail-body">
        <el-descriptions :column="2" border>
          <el-descriptions-item
            v-for="field in detailFields"
            :key="field.prop"
            :label="field.label"
          >
            <img v-if="getSelectIcon(field, detailData)" :src="getSelectIcon(field, detailData)" class="cell-icon" alt="" />
            <span v-else-if="getSelectEmoji(field, detailData)" class="cell-emoji">{{ getSelectEmoji(field, detailData) }}</span>
            {{ formatFieldValue(detailData, field) }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="detail-actions">
          <el-button v-if="userStore.isAdmin" type="primary" @click="handleEditFromDetail">编辑</el-button>
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Add/Edit Drawer -->
    <el-drawer v-model="dialogVisible" :title="editingId ? '编辑' : '新增'" size="60%" :close-on-click-modal="false">
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
      <!-- Extra form content slot (for custom fields like port connection) -->
      <slot name="form-extra" :formData="formData" />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useTableHeight } from '@/composables/useTableHeight'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, View, Close, Operation, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getFormConfigByCode } from '@/api/form_config'
import { resolveSystemFieldOptions } from '@/api/system-field'
import SchemaFormRenderer from '@/components/SchemaFormRenderer.vue'

const props = defineProps({
  api: { type: Object, required: true }, // { list, get, create, update, delete }
  formConfigCode: { type: String, required: true },
  defaultSchema: { type: Array, default: () => [] },
  coreFields: { type: Array, default: () => [] }, // field names that go to top-level (not extra_data)
  columns: { type: Array, default: () => [] }, // core table column definitions
  defaultVisibleColumns: { type: Array, default: () => [] },
  title: { type: String, default: '' },
  entityName: { type: String, default: '记录' },
  nameField: { type: String, default: 'id' },
  searchPlaceholder: { type: String, default: '关键词搜索' },
  storageKey: { type: String, required: true },
})

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const schemaFormRef = ref()
const searchKeyword = ref('')
const searchForm = reactive({})

// 表格区域高度（填满视口，表格内部滚动，整页不下拉）
const tableAreaRef = ref(null)
const { tableHeight } = useTableHeight(tableAreaRef)

// Schema state
const formSchema = ref(props.defaultSchema)
const schemaLoading = ref(false)

// Detail & preview state
const detailVisible = ref(false)
const detailData = ref(null)
const selectedRow = ref(null)

const pagination = reactive({ page: 1, size: 15, total: 0 })
const formData = reactive({})

// ID 排序状态：desc(倒序，默认) / asc(正序)
const sortState = ref('desc')

function onFormUpdate(val) {
  Object.keys(val).forEach((key) => { formData[key] = val[key] })
}

// ===== Load schema from backend =====
async function loadFormSchema() {
  schemaLoading.value = true
  try {
    const config = await getFormConfigByCode(props.formConfigCode)
    if (config && config.form_schema) {
      const parsed = typeof config.form_schema === 'string'
        ? JSON.parse(config.form_schema)
        : config.form_schema
      if (Array.isArray(parsed) && parsed.length > 0) {
        formSchema.value = await resolveSystemFieldOptions(parsed)
      }
    }
  } catch {
    // use default schema
  } finally {
    schemaLoading.value = false
  }
}

// ===== Dynamic fields (from schema, not in core fields) =====
const dynamicTableFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    if (props.coreFields.includes(f.prop)) return false
    if (['id', 'created_at', 'updated_at'].includes(f.prop)) return false
    return true
  })
})

// ===== Column visibility =====
const visibleColumnKeys = ref([])

function initColumnVisibility() {
  try {
    const saved = localStorage.getItem(props.storageKey)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length > 0) {
        visibleColumnKeys.value = parsed
        return
      }
    }
  } catch {}
  visibleColumnKeys.value = [...props.defaultVisibleColumns]
}

watch(visibleColumnKeys, (val) => {
  try { localStorage.setItem(props.storageKey, JSON.stringify(val)) } catch {}
}, { deep: true })

function isColumnVisible(prop) {
  return visibleColumnKeys.value.includes(prop)
}

function toggleColumn(prop) {
  const idx = visibleColumnKeys.value.indexOf(prop)
  if (idx >= 0) visibleColumnKeys.value.splice(idx, 1)
  else visibleColumnKeys.value.push(prop)
}

function resetColumns() {
  visibleColumnKeys.value = [...props.defaultVisibleColumns]
}

const allTableColumns = computed(() => [
  { prop: 'id', label: 'ID' },
  ...props.columns.map(c => ({ prop: c.prop, label: c.label })),
  ...dynamicTableFields.value.map(f => ({ prop: f.prop, label: f.label, dynamic: true })),
  { prop: 'created_at', label: '创建时间' },
])

const visibleCoreColumns = computed(() => {
  return props.columns.filter(c => isColumnVisible(c.prop))
})

const visibleDynamicFields = computed(() => {
  return dynamicTableFields.value.filter(f => isColumnVisible(f.prop))
})

// ===== Preview / Detail fields =====
const previewFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    if (f.prop === props.nameField) return false
    return true
  }).slice(0, 10)
})

const detailFields = computed(() => {
  return formSchema.value.filter((f) => {
    if (['divider', 'alert', 'text'].includes(f.type)) return false
    return true
  })
})

// ===== Helpers =====
function getCellValue(row, prop) {
  let val = row[prop]
  if (val === undefined || val === null) {
    val = row.extra_data?.[prop]
  }
  return val
}

function getTagType(col, row) {
  const val = getCellValue(row, col.prop)
  if (col.tagType) return col.tagType(val)
  if (col.tagMap) return col.tagMap[val] || ''
  return ''
}

// Custom hex color for a tag column (value → color), if provided
function getTagColor(col, row) {
  const val = getCellValue(row, col.prop)
  if (col.colorMap && val != null && val !== '') return col.colorMap[val] || ''
  return ''
}

// Icon (image url) for an icon column
function getIconSrc(col, row) {
  const val = getCellValue(row, col.prop)
  if (col.iconMap && val != null && val !== '') return col.iconMap[val] || ''
  return ''
}

// Emoji fallback for an icon column
function getEmoji(col, row) {
  const val = getCellValue(row, col.prop)
  if (col.emojiMap && val != null && val !== '') return col.emojiMap[val] || ''
  return ''
}

// select-icon 在预览/详情面板中的图标 src（与表格列 type='icon' 不同：从 formSchema.field.options 取）
function getSelectIcon(field, row) {
  if (!row || field.type !== 'select-icon' || !field.options) return ''
  const val = row[field.prop]
  if (val == null || val === '') return ''
  const opt = field.options.find((o) => o.value === val)
  return opt?.icon || ''
}

function getSelectEmoji(field, row) {
  if (!row || field.type !== 'select-icon' || !field.options) return ''
  const val = row[field.prop]
  if (val == null || val === '') return ''
  const opt = field.options.find((o) => o.value === val)
  return opt?.emoji || ''
}

function getTagLabel(col, row) {
  const val = getCellValue(row, col.prop)
  if (col.options) {
    const opt = col.options.find(o => o.value === val)
    return opt ? opt.label : val
  }
  return val
}

function formatFieldValue(row, field) {
  let val = row[field.prop]
  if (val === undefined || val === null) {
    val = row.extra_data?.[field.prop]
  }
  if (val === undefined || val === null || val === '') return '—'
  if ((field.type === 'select' || field.type === 'select-icon') && field.options) {
    const opt = field.options.find(o => o.value === val)
    const label = opt ? opt.label : val
    // select-icon 的图标/emoji 由调用方在 template 里渲染（避免在文本插值中拼 HTML 字符串）
    if (field.type === 'select-icon') {
      return label
    }
    if (Array.isArray(val)) {
      if (val.length === 0) return '—'
      return val.map(v => field.options.find(o => o.value === v)?.label || v).join(', ')
    }
    return label
  }
  if (field.type === 'date') return formatDate(val)
  if (field.type === 'datetime') return formatDateTime(val)
  if (Array.isArray(val)) return val.length === 0 ? '—' : val.join(', ')
  return val
}

function formatDate(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function formatDateTime(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ===== Data Fetching =====
async function fetchData() {
  loading.value = true
  try {
    const data = await props.api.list({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      keyword: searchKeyword.value || undefined,
      order: sortState.value,
    })
    tableData.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

// 点击 ID 列头切换排序：column 为 null（其它列）忽略；id 列在 desc/asc 间循环
function handleSortChange({ prop, order }) {
  if (prop !== 'id') return
  // order: 'ascending' | 'descending' | null；循环：desc→asc→desc
  sortState.value = sortState.value === 'desc' ? 'asc' : 'desc'
  fetchData()
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchKeyword.value = ''
  Object.keys(searchForm).forEach(k => delete searchForm[k])
  handleSearch()
}

function handleRowClick(row) {
  selectedRow.value = row
}

async function handleDetail(row) {
  try {
    detailData.value = await props.api.get(row.id)
  } catch {
    detailData.value = row
  }
  detailVisible.value = true
}

function handleEditFromDetail() {
  if (!detailData.value) return
  detailVisible.value = false
  handleEdit(detailData.value)
}

function handleAdd() {
  editingId.value = null
  Object.keys(formData).forEach(k => delete formData[k])
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.keys(formData).forEach(k => delete formData[k])
  const extra = row.extra_data || {}
  formSchema.value.forEach((field) => {
    if (['divider', 'alert', 'text'].includes(field.type)) return
    let val = row[field.prop]
    if (val === undefined || val === null) val = extra[field.prop]
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
    const payload = {}
    const extraData = {}
    formSchema.value.forEach((field) => {
      if (['divider', 'alert', 'text'].includes(field.type)) return
      const val = formData[field.prop]
      if (props.coreFields.includes(field.prop)) {
        payload[field.prop] = (val !== undefined && val !== '' && val !== null) ? val : null
      } else {
        if (val !== undefined && val !== '' && val !== null) {
          extraData[field.prop] = val
        }
      }
    })
    payload.extra_data = Object.keys(extraData).length > 0 ? extraData : null

    if (editingId.value) {
      await props.api.update(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await props.api.create(payload)
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
  const name = getCellValue(row, props.nameField) || `ID:${row.id}`
  await ElMessageBox.confirm(`确定要删除「${name}」吗？`, '删除确认', { type: 'warning' })
  await props.api.delete(row.id)
  ElMessage.success('删除成功')
  if (selectedRow.value?.id === row.id) selectedRow.value = null
  fetchData()
}

onMounted(() => {
  initColumnVisibility()
  loadFormSchema()
  fetchData()
})
</script>

<style scoped>
.qp-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }
.qp-header span { display: flex; align-items: center; gap: 6px; }
.qp-body { display: flex; flex-direction: column; gap: 14px; }
.qp-name { font-size: 18px; font-weight: 700; padding-bottom: 10px; border-bottom: 1px solid var(--el-border-color-lighter); }
.qp-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qp-info-item { display: flex; flex-direction: column; gap: 2px; }
.qp-label { font-size: 11px; color: var(--el-text-color-secondary); text-transform: uppercase; letter-spacing: 0.3px; }
.qp-value { font-size: 13px; font-weight: 500; word-break: break-all; }
.qp-actions { display: flex; gap: 8px; }
.qp-hint { font-size: 12px; color: var(--el-text-color-placeholder); }
.slide-preview-enter-active, .slide-preview-leave-active { transition: all 0.3s ease; }
.slide-preview-enter-from, .slide-preview-leave-to { opacity: 0; transform: translateX(20px); }
.detail-body { padding: 0 4px; display: flex; flex-direction: column; gap: 20px; }
.detail-actions { display: flex; gap: 10px; padding-top: 8px; }
.schema-loading { display: flex; align-items: center; gap: 8px; justify-content: center; padding: 60px 0; color: var(--el-text-color-secondary); font-size: 14px; }
.schema-loading .is-loading { font-size: 20px; }
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

/* ===== Icon column + colored tag ===== */
.cell-icon-wrap, .cell-tag-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.cell-icon {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  object-fit: contain;
  flex-shrink: 0;
}
.cell-emoji {
  font-size: 16px;
  line-height: 1;
}
</style>
