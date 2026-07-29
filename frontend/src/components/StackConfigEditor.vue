<template>
  <div class="stack-config-editor">
    <div class="sc-switch-row">
      <el-switch v-model="local.enabled" inline-prompt active-text="开启" inactive-text="关闭" @change="onEnabledChange" />
      <span class="sc-hint">开启堆叠后，按数量自动生成堆叠成员。成员1自动继承本机序列号/资产编码/财务编码，其余成员默认"—"需人工填写</span>
    </div>

    <template v-if="local.enabled">
      <el-form-item label="堆叠数量" label-width="90px" class="sc-count-item">
        <el-input-number v-model="local.count" :min="2" :max="16" @change="regenerateMembers" />
        <span class="sc-hint" style="margin-left: 12px">台（含本机，建议 2~16）</span>
      </el-form-item>

      <div class="sc-table-title">
        <span>堆叠成员列表（可手动修改）</span>
        <el-button size="small" text type="primary" @click="regenerateMembers">重新生成</el-button>
      </div>

      <el-alert
        v-if="hasDuplicates"
        type="error"
        :closable="false"
        show-icon
        title="序列号 / IT资产编码 / 财务资产编码 存在重复，请修改后再保存"
        style="margin-bottom: 10px"
      />

        <el-table :data="local.members" border size="small">
        <el-table-column label="成员" width="64">
          <template #default="{ $index }">#{{ $index + 1 }}</template>
        </el-table-column>
        <el-table-column label="设备名称" min-width="170">
          <template #default="{ row }">
            <el-input v-model="row.name" size="small" placeholder="设备名称" />
          </template>
        </el-table-column>
        <el-table-column label="序列号" min-width="160">
          <template #default="{ row, $index }">
            <el-input
              v-model="row.serial_number"
              size="small"
              placeholder="—（人工填写）"
              :class="{ 'sc-input-error': duplicateFlags[`${$index}__serial_number`] }"
              @change="onMemberFieldChange('serial_number', row, $index)"
            />
            <div v-if="duplicateFlags[`${$index}__serial_number`]" class="sc-dup-tip">不可重复</div>
          </template>
        </el-table-column>
        <el-table-column label="IT资产编码" min-width="150">
          <template #default="{ row, $index }">
            <el-input
              v-model="row.it_asset_code"
              size="small"
              placeholder="—（人工填写）"
              :class="{ 'sc-input-error': duplicateFlags[`${$index}__it_asset_code`] }"
              @change="onMemberFieldChange('it_asset_code', row, $index)"
            />
            <div v-if="duplicateFlags[`${$index}__it_asset_code`]" class="sc-dup-tip">不可重复</div>
          </template>
        </el-table-column>
        <el-table-column label="财务资产编码" min-width="150">
          <template #default="{ row, $index }">
            <el-input
              v-model="row.financial_asset_code"
              size="small"
              placeholder="—（人工填写）"
              :class="{ 'sc-input-error': duplicateFlags[`${$index}__financial_asset_code`] }"
              @change="onMemberFieldChange('financial_asset_code', row, $index)"
            />
            <div v-if="duplicateFlags[`${$index}__financial_asset_code`]" class="sc-dup-tip">不可重复</div>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { summarizePortGroups } from '@/utils/portNaming'

const props = defineProps({
  modelValue: { type: [Object, Array], default: () => ({ enabled: false, count: 0, members: [] }) },
  formData: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

// Fields that must be unique across stacking members (declared before mount-time
// syncPrevious() so they are initialized and not in the temporal dead zone).
const UNIQUE_FIELDS = ['serial_number', 'it_asset_code', 'financial_asset_code']
const FIELD_LABELS = {
  serial_number: '序列号',
  it_asset_code: 'IT资产编码',
  financial_asset_code: '财务资产编码',
}
const previousValues = reactive({})

function normalize(v) {
  if (!v || typeof v !== 'object' || Array.isArray(v)) {
    return { enabled: false, count: 0, members: [] }
  }
  return {
    enabled: !!v.enabled,
    count: Number(v.count) || 0,
    members: Array.isArray(v.members) ? v.members : [],
  }
}

const local = ref(normalize(props.modelValue))
syncPrevious()

watch(
  () => props.modelValue,
  (v) => {
    if (v !== local.value) {
      local.value = normalize(v)
      syncPrevious()
    }
  },
)

const baseName = computed(() => (props.formData?.device_name || '').trim())
const portSummary = computed(() => summarizePortGroups(props.formData?.port_groups))

/** Strip a trailing `-<digits>` so "YF2F-ACC-SW-1" -> "YF2F-ACC-SW". */
function stripTrailingNum(name) {
  if (!name) return ''
  return name.replace(/-\d+$/, '')
}

function sync() {
  emit('update:modelValue', local.value)
}

function buildMembers(count) {
  const base = stripTrailingNum(baseName.value) || '交换机'
  // Member 1 inherits the device's own serial / IT code / financial code.
  const devSerial = props.formData?.serial_number || ''
  const devIt = props.formData?.it_asset_code || ''
  const devFa = props.formData?.financial_asset_code || ''
  const list = []
  for (let m = 1; m <= count; m++) {
    const isFirst = m === 1
    list.push({
      name: `${base}-${m}`,
      // Member 1 auto-adopts the device's values; others default to "—" (manual fill).
      serial_number: isFirst ? devSerial : '—',
      it_asset_code: isFirst ? devIt : '—',
      financial_asset_code: isFirst ? devFa : '—',
    })
  }
  return list
}

function regenerateMembers() {
  const count = Math.max(2, Number(local.value.count) || 2)
  local.value.count = count
  // Preserve existing member edits where possible
  const existing = local.value.members || []
  const next = buildMembers(count)
  for (let i = 0; i < next.length; i++) {
    if (existing[i]) {
      next[i].name = existing[i].name || next[i].name
      // Keep manual edits to code fields unless the user left them empty/"—"
      if (existing[i].serial_number && existing[i].serial_number !== '—') next[i].serial_number = existing[i].serial_number
      if (existing[i].it_asset_code && existing[i].it_asset_code !== '—') next[i].it_asset_code = existing[i].it_asset_code
      if (existing[i].financial_asset_code && existing[i].financial_asset_code !== '—') next[i].financial_asset_code = existing[i].financial_asset_code
    }
  }
  local.value.members = next
  syncPrevious()
  sync()
}

function onEnabledChange(val) {
  if (val) {
    regenerateMembers()
  } else {
    local.value.members = []
    syncPrevious()
    sync()
  }
}

// ===== Uniqueness for serial_number / it_asset_code / financial_asset_code =====
// (UNIQUE_FIELDS / FIELD_LABELS / previousValues are declared above, before mount)

// Track previous values so a duplicate entry can be reverted (拒绝重复填写).
function syncPrevious() {
  const map = {}
  ;(local.value.members || []).forEach((m, i) => {
    UNIQUE_FIELDS.forEach((f) => {
      map[`${i}__${f}`] = (m[f] ?? '').trim()
    })
  })
  Object.keys(previousValues).forEach((k) => delete previousValues[k])
  Object.assign(previousValues, map)
}

// Block duplicate values at input time: if the new value already exists on another
// member, revert and warn (满足「有重复不给填写」).
function onMemberFieldChange(field, row, index) {
  const key = `${index}__${field}`
  const raw = (row[field] ?? '').trim()
  const prev = previousValues[key]
  previousValues[key] = raw
  if (!raw || raw === '—') {
    sync()
    return
  }
  const dup = (local.value.members || []).some(
    (m, i) => i !== index && (m[field] ?? '').trim() === raw,
  )
  if (dup) {
    row[field] = prev ?? '—'
    previousValues[key] = prev ?? '—'
    ElMessage.warning(`${FIELD_LABELS[field]}「${raw}」已存在，不能重复填写`)
  }
  sync()
}

// Flag duplicate values for inline display (also catches pre-existing duplicates).
const duplicateFlags = computed(() => {
  const flags = {}
  const members = local.value.members || []
  UNIQUE_FIELDS.forEach((f) => {
    const seen = {}
    members.forEach((m, i) => {
      const v = (m[f] ?? '').trim()
      if (!v || v === '—') return
      if (seen[v] !== undefined) {
        flags[`${i}__${f}`] = true
        flags[`${seen[v]}__${f}`] = true
      } else {
        seen[v] = i
      }
    })
  })
  return flags
})

const hasDuplicates = computed(() => Object.keys(duplicateFlags.value).length > 0)

// Exposed to the parent form so it can block saving when duplicates exist.
function validateStack() {
  if (hasDuplicates.value) {
    ElMessage.warning('堆叠成员的序列号 / IT资产编码 / 财务资产编码 不能重复，请修改后再保存')
    return false
  }
  return true
}

defineExpose({ validate: validateStack })
</script>

<style scoped>
.stack-config-editor { width: 100%; }
.sc-switch-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.sc-hint { font-size: 12px; color: var(--el-text-color-secondary); }
.sc-count-item { margin-bottom: 8px; }
.sc-table-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 600;
  margin: 8px 0 10px;
}
.sc-input-error :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--el-color-danger) inset;
}
.sc-dup-tip {
  color: var(--el-color-danger);
  font-size: 12px;
  line-height: 1.4;
  margin-top: 2px;
}
</style>
