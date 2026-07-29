<template>
  <el-form :model="formData" :rules="rules" label-width="100px" ref="formRef">
    <el-row :gutter="16">
      <el-col
        v-for="field in visibleFields"
        :key="field.id || field.prop"
        :span="field.span || 24"
      >
        <!-- Layout fields: no form-item wrapper -->
        <template v-if="isLayoutField(field.type)">
          <el-divider v-if="field.type === 'divider'" content-position="left">
            {{ field.label }}
          </el-divider>
          <el-alert
            v-else-if="field.type === 'alert'"
            :title="field.placeholder || field.label || '提示信息'"
            :type="field.alertType || 'info'"
            :closable="false"
            show-icon
            style="margin-bottom: 12px"
          />
          <div v-else-if="field.type === 'text'" class="text-render">
            {{ field.defaultValue || field.placeholder || '' }}
          </div>
        </template>

        <!-- Form fields -->
        <el-form-item
          v-else
          :label="field.label"
          :prop="field.prop"
          :required="field.required"
        >
          <!-- Input -->
          <el-input
            v-if="field.type === 'input'"
            v-model="formData[field.prop]"
            :placeholder="field.placeholder"
            :clearable="true"
          />
          <!-- Password -->
          <el-input
            v-else-if="field.type === 'password'"
            v-model="formData[field.prop]"
            type="password"
            show-password
            :placeholder="field.placeholder"
          />
          <!-- Textarea -->
          <el-input
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.prop]"
            type="textarea"
            :rows="field.rows || 3"
            :placeholder="field.placeholder"
            maxlength="500"
            show-word-limit
          />
          <!-- Number -->
          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="formData[field.prop]"
            :min="field.min"
            :max="field.max"
            style="width: 100%"
          />
          <!-- Select -->
          <el-select
            v-else-if="field.type === 'select'"
            v-model="formData[field.prop]"
            :placeholder="field.placeholder"
            style="width: 100%"
            :clearable="true"
            :filterable="true"
          >
            <el-option
              v-for="opt in field.options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <!-- Radio -->
          <el-radio-group
            v-else-if="field.type === 'radio'"
            v-model="formData[field.prop]"
          >
            <el-radio
              v-for="opt in field.options"
              :key="opt.value"
              :value="opt.value"
            >{{ opt.label }}</el-radio>
          </el-radio-group>
          <!-- Checkbox -->
          <el-checkbox-group
            v-else-if="field.type === 'checkbox'"
            v-model="formData[field.prop]"
          >
            <el-checkbox
              v-for="opt in field.options"
              :key="opt.value"
              :value="opt.value"
            >{{ opt.label }}</el-checkbox>
          </el-checkbox-group>
          <!-- Switch -->
          <el-switch
            v-else-if="field.type === 'switch'"
            v-model="formData[field.prop]"
            inline-prompt
            active-text="是"
            inactive-text="否"
          />
          <!-- Date -->
          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="formData[field.prop]"
            type="date"
            value-format="YYYY-MM-DD"
            :placeholder="field.placeholder || '请选择日期'"
            style="width: 100%"
          />
          <!-- DateTime -->
          <el-date-picker
            v-else-if="field.type === 'datetime'"
            v-model="formData[field.prop]"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            :placeholder="field.placeholder || '请选择日期时间'"
            style="width: 100%"
          />
          <!-- DateRange -->
          <el-date-picker
            v-else-if="field.type === 'daterange'"
            v-model="formData[field.prop]"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
          <!-- Time -->
          <el-time-picker
            v-else-if="field.type === 'time'"
            v-model="formData[field.prop]"
            value-format="HH:mm:ss"
            :placeholder="field.placeholder || '请选择时间'"
            style="width: 100%"
          />
          <!-- Cascader -->
          <el-cascader
            v-else-if="field.type === 'cascader'"
            v-model="formData[field.prop]"
            :options="field.cascaderOptions || []"
            :placeholder="field.placeholder"
            style="width: 100%"
            :clearable="true"
          />
          <!-- Rate -->
          <el-rate
            v-else-if="field.type === 'rate'"
            v-model="formData[field.prop]"
            :max="field.max || 5"
            show-text
            :texts="['很差', '较差', '一般', '较好', '很好']"
          />
          <!-- Slider -->
          <el-slider
            v-else-if="field.type === 'slider'"
            v-model="formData[field.prop]"
            :min="field.min"
            :max="field.max"
            :step="field.step || 1"
            show-input
          />
          <!-- Color -->
          <el-color-picker
            v-else-if="field.type === 'color'"
            v-model="formData[field.prop]"
            show-alpha
          />
          <!-- Upload -->
          <el-upload
            v-else-if="field.type === 'upload'"
            :action="field.uploadUrl || '/api/upload'"
            :limit="field.maxCount || 5"
            :list-type="field.listType || 'text'"
            :on-success="(res, file) => handleUploadSuccess(field.prop, res, file)"
            :on-remove="(file) => handleUploadRemove(field.prop, file)"
            :file-list="formData[field.prop] || []"
          >
            <el-button type="primary" size="small">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">{{ field.placeholder || '支持上传文件' }}</div>
            </template>
          </el-upload>
          <!-- Transfer -->
          <el-transfer
            v-else-if="field.type === 'transfer'"
            v-model="formData[field.prop]"
            :data="(field.options || []).map((o, i) => ({ key: o.value, label: o.label }))"
            :titles="['可选', '已选']"
          />
          <!-- Tag Input -->
          <div v-else-if="field.type === 'tag'" class="tag-input-wrapper">
            <el-tag
              v-for="(tag, ti) in (formData[field.prop] || [])"
              :key="ti"
              closable
              :disable-transitions="false"
              @close="removeTag(field.prop, ti)"
              style="margin-right: 6px; margin-bottom: 4px"
            >{{ tag }}</el-tag>
            <el-input
              v-if="tagInputVisible[field.prop]"
              v-model="tagInputValue[field.prop]"
              size="small"
              style="width: 120px"
              @keyup.enter="confirmTag(field.prop)"
              @blur="confirmTag(field.prop)"
            />
            <el-button
              v-else
              size="small"
              @click="showTagInput(field.prop)"
            >+ 添加标签</el-button>
          </div>
          <!-- Port Groups (custom: switch port config by type) -->
          <port-groups-editor
            v-else-if="field.type === 'portGroups'"
            v-model="formData[field.prop]"
          />
          <!-- Stack Config (custom: switch stacking members) -->
          <stack-config-editor
            v-else-if="field.type === 'stackConfig'"
            ref="stackEditorRef"
            v-model="formData[field.prop]"
            :form-data="formData"
          />
          <!-- Fallback -->
          <el-input v-else v-model="formData[field.prop]" :placeholder="field.placeholder" />
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script setup>
import { ref, reactive, watch, computed, nextTick } from 'vue'
import PortGroupsEditor from './PortGroupsEditor.vue'
import StackConfigEditor from './StackConfigEditor.vue'

const props = defineProps({
  fields: { type: Array, default: () => [] },
  modelValue: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue'])

const formRef = ref()
const stackEditorRef = ref()
const formData = reactive({ ...props.modelValue })

// Flag to prevent watch sync loops (parent ↔ child)
let syncing = false

// Tag input state
const tagInputVisible = reactive({})
const tagInputValue = reactive({})

function isLayoutField(type) {
  return ['divider', 'alert', 'text'].includes(type)
}

// ==================== Conditional Visibility ====================
// Supports: { visibleWhen: { prop: 'device_type', equals: 'switch' } }
// Also supports: { visibleWhen: { prop: 'device_type', in: ['switch', 'router'] } }
function isFieldVisible(field, data = formData) {
  if (!field.visibleWhen) return true
  const cond = field.visibleWhen
  const val = data[cond.prop]
  if (cond.equals !== undefined) return val === cond.equals
  if (cond.in !== undefined) return cond.in.includes(val)
  if (cond.notEquals !== undefined) return val !== cond.notEquals
  return true
}

const visibleFields = computed(() => {
  return props.fields.filter((field) => isFieldVisible(field))
})

// Initialize form data with defaults (only for currently visible fields)
function initDefaults() {
  props.fields.forEach((f) => {
    if (isLayoutField(f.type)) return
    // Skip invisible conditional fields so they don't get submitted as extra_data
    if (!isFieldVisible(f)) return
    if (formData[f.prop] === undefined) {
      if (f.defaultValue !== '' && f.defaultValue !== undefined && f.defaultValue !== null) {
        if (f.type === 'number' || f.type === 'rate' || f.type === 'slider') {
          formData[f.prop] = Number(f.defaultValue)
        } else if (f.type === 'switch') {
          formData[f.prop] = f.defaultValue === true || f.defaultValue === 'true'
        } else {
          formData[f.prop] = f.defaultValue
        }
      } else if (f.type === 'checkbox' || f.type === 'transfer' || f.type === 'daterange') {
        formData[f.prop] = []
      } else if (f.type === 'switch') {
        formData[f.prop] = false
      } else if (f.type === 'tag') {
        formData[f.prop] = [...(f.defaultTags || [])]
      } else if (f.type === 'upload') {
        formData[f.prop] = []
      } else if (f.type === 'rate') {
        formData[f.prop] = 0
      } else if (f.type === 'slider') {
        formData[f.prop] = f.min || 0
      } else if (f.type === 'color') {
        formData[f.prop] = ''
      } else if (f.type === 'portGroups') {
        formData[f.prop] = []
      } else if (f.type === 'stackConfig') {
        formData[f.prop] = { enabled: false, count: 0, members: [] }
      } else {
        formData[f.prop] = ''
      }
    }
  })
}
initDefaults()

// Re-init when fields change
watch(() => props.fields, () => {
  initDefaults()
}, { deep: true })

// Sync from parent → child (when parent updates modelValue externally, e.g. on edit)
watch(() => props.modelValue, (newVal) => {
  if (syncing) return
  if (!newVal) return
  syncing = true
  const newKeys = Object.keys(newVal)
  newKeys.forEach((key) => {
    formData[key] = newVal[key]
  })
  Object.keys(formData).forEach((key) => {
    if (!newKeys.includes(key)) delete formData[key]
  })
  // Re-initialize defaults for any fields not provided by parent
  // This ensures default values (e.g. status='in_use') are restored after clear
  initDefaults()
  nextTick(() => { syncing = false })
}, { deep: true })

// Sync from child → parent
watch(formData, (val) => {
  if (syncing) return
  syncing = true
  emit('update:modelValue', { ...val })
  nextTick(() => { syncing = false })
}, { deep: true })

// Build validation rules from schema
const rules = computed(() => {
  const r = {}
  props.fields.forEach((f) => {
    if (isLayoutField(f.type)) return
    if (f.required) {
      const trigger = ['select', 'radio', 'checkbox', 'date', 'datetime', 'time', 'cascader', 'switch', 'rate', 'slider', 'color'].includes(f.type) ? 'change' : 'blur'
      r[f.prop] = [{
        required: true,
        message: f.type === 'checkbox' || f.type === 'transfer' || f.type === 'upload'
          ? `请选择${f.label}`
          : `请输入${f.label}`,
        trigger,
      }]
    }
  })
  return r
})

// ==================== Tag Input ====================
function showTagInput(prop) {
  tagInputVisible[prop] = true
  tagInputValue[prop] = ''
}

function confirmTag(prop) {
  const val = tagInputValue[prop]?.trim()
  if (val && !formData[prop].includes(val)) {
    formData[prop].push(val)
  }
  tagInputVisible[prop] = false
  tagInputValue[prop] = ''
}

function removeTag(prop, index) {
  formData[prop].splice(index, 1)
}

// ==================== Upload ====================
function handleUploadSuccess(prop, response, file) {
  if (!formData[prop]) formData[prop] = []
  formData[prop].push({ name: file.name, url: file.url || response?.url || '', uid: file.uid })
}

function handleUploadRemove(prop, file) {
  const idx = (formData[prop] || []).findIndex((f) => f.uid === file.uid || f.name === file.name)
  if (idx > -1) formData[prop].splice(idx, 1)
}

// Expose validate method: runs el-form validation, then the custom stack-config
// uniqueness check. Rejects (throws) when duplicates exist so the parent blocks save.
async function doValidate(...args) {
  await formRef.value?.validate(...args)
  const stackOk = await stackEditorRef.value?.validate?.()
  if (stackOk === false) {
    throw new Error('堆叠成员存在重复编码')
  }
}

defineExpose({
  validate: doValidate,
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData }),
})
</script>

<style scoped>
.tag-input-wrapper {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.text-render {
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
  padding: 4px 0;
}
</style>
