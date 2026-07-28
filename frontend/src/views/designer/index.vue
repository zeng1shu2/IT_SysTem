<template>
  <div class="designer-page">
    <!-- ===== Top Toolbar ===== -->
    <div class="designer-toolbar">
      <div class="toolbar-left">
        <el-input v-model="formName" placeholder="表单名称" style="width: 200px" />
        <el-input v-model="formCode" placeholder="表单编码（英文）" style="width: 180px" />
        <el-input v-model="formDesc" placeholder="表单描述" style="width: 240px" />
        <el-button text @click="newForm">
          <el-icon><Plus /></el-icon> 新建
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button @click="handlePreview">
          <el-icon><View /></el-icon> 预览
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon> 导出JSON
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon> 导入JSON
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon> 保存
        </el-button>
      </div>
    </div>

    <!-- ===== Three Column Layout ===== -->
    <div class="designer-body">
      <!-- ===== Left: Field Palette ===== -->
      <div class="palette-panel">
        <div v-for="group in fieldGroups" :key="group.title" style="margin-bottom: 16px">
          <div class="panel-title">{{ group.title }}</div>
          <div class="palette-grid">
            <div
              v-for="ft in group.items"
              :key="ft.type"
              class="palette-item"
              @click="addField(ft)"
            >
              <el-icon class="palette-icon"><component :is="ft.icon" /></el-icon>
              <span>{{ ft.label }}</span>
            </div>
          </div>
        </div>

        <div class="panel-title">已保存表单</div>
        <div class="saved-list">
          <div
            v-for="item in savedForms"
            :key="item.id"
            class="saved-item"
            :class="{ active: editingId === item.id }"
            @click="loadForm(item)"
          >
            <span class="saved-name">{{ item.name }}</span>
            <el-button size="small" type="danger" text @click.stop="handleDeleteSaved(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <div v-if="savedForms.length === 0" class="empty-hint">暂无保存的表单</div>
        </div>
      </div>

      <!-- ===== Center: Canvas ===== -->
      <div class="canvas-panel">
        <div class="canvas-header">
          <span>表单画布</span>
          <el-button text size="small" @click="clearFields" v-if="fields.length">清空</el-button>
        </div>
        <div class="canvas-body" @click.self="selectField(-1)">
          <div v-if="fields.length === 0" class="canvas-empty">
            <el-icon size="48"><Plus /></el-icon>
            <p>点击左侧字段类型添加字段</p>
          </div>
          <div
            v-for="(field, index) in fields"
            :key="field.id"
            class="canvas-field"
            :class="{ selected: selectedIndex === index, 'is-layout': isLayoutField(field.type) }"
            @click.stop="selectField(index)"
          >
            <div class="field-handle">
              <el-icon><Rank /></el-icon>
            </div>
            <div class="field-content">
              <el-form label-width="100px" size="small" disabled>
                <el-form-item :label="field.label" :required="field.required">
                  <!-- Input -->
                  <el-input v-if="field.type === 'input'" :placeholder="field.placeholder" :model-value="field.defaultValue" />
                  <!-- Password -->
                  <el-input v-else-if="field.type === 'password'" type="password" show-password :placeholder="field.placeholder" :model-value="field.defaultValue" />
                  <!-- Textarea -->
                  <el-input v-else-if="field.type === 'textarea'" type="textarea" :rows="field.rows || 3" :placeholder="field.placeholder" :model-value="field.defaultValue" />
                  <!-- Number -->
                  <el-input-number v-else-if="field.type === 'number'" :min="field.min" :max="field.max" :model-value="field.defaultValue ? Number(field.defaultValue) : undefined" style="width: 100%" />
                  <!-- Select -->
                  <el-select v-else-if="field.type === 'select'" :placeholder="field.placeholder" style="width: 100%" :model-value="field.defaultValue">
                    <el-option v-for="opt in field.options" :key="opt.value" :label="opt.label" :value="opt.value" />
                  </el-select>
                  <!-- Radio -->
                  <el-radio-group v-else-if="field.type === 'radio'" :model-value="field.defaultValue">
                    <el-radio v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</el-radio>
                  </el-radio-group>
                  <!-- Checkbox -->
                  <el-checkbox-group v-else-if="field.type === 'checkbox'" :model-value="field.defaultValue ? [field.defaultValue] : []">
                    <el-checkbox v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</el-checkbox>
                  </el-checkbox-group>
                  <!-- Switch -->
                  <el-switch v-else-if="field.type === 'switch'" :model-value="!!field.defaultValue" />
                  <!-- Date -->
                  <el-date-picker v-else-if="field.type === 'date'" type="date" value-format="YYYY-MM-DD" :placeholder="field.placeholder" style="width: 100%" :model-value="field.defaultValue" />
                  <!-- DateTime -->
                  <el-date-picker v-else-if="field.type === 'datetime'" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" :placeholder="field.placeholder" style="width: 100%" :model-value="field.defaultValue" />
                  <!-- DateRange -->
                  <el-date-picker v-else-if="field.type === 'daterange'" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 100%" :model-value="field.defaultValue" />
                  <!-- Time -->
                  <el-time-picker v-else-if="field.type === 'time'" value-format="HH:mm:ss" :placeholder="field.placeholder" style="width: 100%" :model-value="field.defaultValue" />
                  <!-- Cascader -->
                  <el-cascader v-else-if="field.type === 'cascader'" :options="field.cascaderOptions || []" :placeholder="field.placeholder" style="width: 100%" :model-value="field.defaultValue" />
                  <!-- Rate -->
                  <el-rate v-else-if="field.type === 'rate'" :max="field.max || 5" :model-value="Number(field.defaultValue) || 0" />
                  <!-- Slider -->
                  <el-slider v-else-if="field.type === 'slider'" :min="field.min" :max="field.max" :step="field.step || 1" :model-value="Number(field.defaultValue) || 0" />
                  <!-- Color -->
                  <el-color-picker v-else-if="field.type === 'color'" :model-value="field.defaultValue" />
                  <!-- Upload -->
                  <el-upload v-else-if="field.type === 'upload'" :action="field.uploadUrl || '#'" :limit="field.maxCount || 5" :list-type="field.listType || 'text'" disabled>
                    <el-button size="small" type="primary" disabled>点击上传</el-button>
                  </el-upload>
                  <!-- Transfer -->
                  <el-transfer v-else-if="field.type === 'transfer'" :data="(field.options || []).map((o, i) => ({ key: o.value, label: o.label }))" v-model="transferPreview" />
                  <!-- Tag Input -->
                  <div v-else-if="field.type === 'tag'" class="tag-preview">
                    <el-tag v-for="t in (field.defaultTags || ['标签1', '标签2'])" :key="t" closable>{{ t }}</el-tag>
                  </div>
                  <!-- Divider (layout) -->
                  <el-divider v-else-if="field.type === 'divider'" content-position="left">{{ field.label }}</el-divider>
                  <!-- Alert (layout) -->
                  <el-alert v-else-if="field.type === 'alert'" :title="field.placeholder || '提示信息'" :type="field.alertType || 'info'" :closable="false" show-icon />
                  <!-- Text display (layout) -->
                  <span v-else-if="field.type === 'text'" class="text-display">{{ field.defaultValue || field.placeholder || '纯文本展示区域' }}</span>
                  <!-- Fallback -->
                  <el-input v-else :placeholder="field.placeholder" />
                </el-form-item>
              </el-form>
            </div>
            <div class="field-actions">
              <el-button size="small" text @click.stop="moveUp(index)" :disabled="index === 0">
                <el-icon><Top /></el-icon>
              </el-button>
              <el-button size="small" text @click.stop="moveDown(index)" :disabled="index === fields.length - 1">
                <el-icon><Bottom /></el-icon>
              </el-button>
              <el-button size="small" text @click.stop="duplicateField(index)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
              <el-button size="small" text type="danger" @click.stop="removeField(index)">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== Right: Property Panel ===== -->
      <div class="property-panel">
        <div class="panel-title">字段属性</div>
        <div v-if="selectedIndex === -1" class="empty-hint">请选择一个字段进行编辑</div>
        <el-form v-else label-position="top" size="small">
          <el-form-item label="字段类型">
            <el-tag>{{ getTypeLabel(fields[selectedIndex].type) }}</el-tag>
          </el-form-item>
          <el-form-item label="字段标签">
            <el-input v-model="fields[selectedIndex].label" />
          </el-form-item>
          <el-form-item label="字段名（prop）" v-if="!isLayoutField(fields[selectedIndex].type)">
            <el-input v-model="fields[selectedIndex].prop" placeholder="如：device_name" />
          </el-form-item>
          <el-form-item label="占位提示" v-if="!isLayoutField(fields[selectedIndex].type)">
            <el-input v-model="fields[selectedIndex].placeholder" />
          </el-form-item>
          <el-form-item label="默认值" v-if="hasDefaultValue(fields[selectedIndex].type)">
            <el-input v-if="['input', 'textarea', 'password', 'date', 'datetime', 'time', 'color'].includes(fields[selectedIndex].type)"
              v-model="fields[selectedIndex].defaultValue" />
            <el-input-number v-else-if="fields[selectedIndex].type === 'number'"
              v-model="fields[selectedIndex].defaultValue" style="width: 100%" />
            <el-input-number v-else-if="fields[selectedIndex].type === 'rate'"
              v-model="fields[selectedIndex].defaultValue" :min="0" :max="fields[selectedIndex].max || 5" style="width: 100%" />
            <el-input-number v-else-if="fields[selectedIndex].type === 'slider'"
              v-model="fields[selectedIndex].defaultValue" :min="fields[selectedIndex].min" :max="fields[selectedIndex].max" style="width: 100%" />
            <el-switch v-else-if="fields[selectedIndex].type === 'switch'"
              v-model="fields[selectedIndex].defaultValue" />
          </el-form-item>
          <el-form-item label="必填" v-if="!isLayoutField(fields[selectedIndex].type)">
            <el-switch v-model="fields[selectedIndex].required" />
          </el-form-item>

          <!-- Conditional Visibility -->
          <el-form-item label="条件显示" v-if="!isLayoutField(fields[selectedIndex].type)">
            <div class="visible-when-config">
              <el-switch
                :model-value="!!fields[selectedIndex].visibleWhen"
                @change="(val) => toggleVisibleWhen(fields[selectedIndex], val)"
              />
              <template v-if="fields[selectedIndex].visibleWhen">
                <div class="vw-row">
                  <span class="vw-label">当</span>
                  <el-input
                    v-model="fields[selectedIndex].visibleWhen.prop"
                    placeholder="依赖字段prop"
                    size="small"
                    style="width: 120px"
                  />
                </div>
                <div class="vw-row">
                  <el-select v-model="fields[selectedIndex].visibleWhen._op" size="small" style="width: 100px" @change="onVisibleWhenOpChange(fields[selectedIndex])">
                    <el-option label="等于" value="equals" />
                    <el-option label="不等于" value="notEquals" />
                    <el-option label="属于" value="in" />
                  </el-select>
                </div>
                <div class="vw-row" v-if="fields[selectedIndex].visibleWhen._op !== 'in'">
                  <el-input
                    v-model="fields[selectedIndex].visibleWhen.equals"
                    placeholder="值"
                    size="small"
                    v-if="fields[selectedIndex].visibleWhen._op === 'equals'"
                  />
                  <el-input
                    v-model="fields[selectedIndex].visibleWhen.notEquals"
                    placeholder="值"
                    size="small"
                    v-else
                  />
                </div>
                <div class="vw-row" v-else>
                  <el-input
                    v-model="fields[selectedIndex].visibleWhen._inStr"
                    placeholder="值1,值2,值3"
                    size="small"
                    @blur="parseVisibleWhenIn(fields[selectedIndex])"
                  />
                </div>
              </template>
            </div>
          </el-form-item>
          <el-form-item label="宽度" v-if="!isLayoutField(fields[selectedIndex].type) && fields[selectedIndex].type !== 'textarea'">
            <el-radio-group v-model="fields[selectedIndex].span">
              <el-radio-button :value="24">整行</el-radio-button>
              <el-radio-button :value="12">半行</el-radio-button>
              <el-radio-button :value="8">三分之一</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <!-- Options editor for select/radio/checkbox/transfer -->
          <template v-if="['select', 'radio', 'checkbox', 'transfer'].includes(fields[selectedIndex].type)">
            <el-form-item label="选项列表">
              <div class="options-editor">
                <div v-for="(opt, oi) in fields[selectedIndex].options" :key="oi" class="option-row">
                  <el-input v-model="opt.label" placeholder="显示文本" size="small" style="width: 45%" />
                  <el-input v-model="opt.value" placeholder="值" size="small" style="width: 45%" />
                  <el-button size="small" text type="danger" @click="fields[selectedIndex].options.splice(oi, 1)">
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
                <el-button size="small" @click="addOption(fields[selectedIndex])">
                  <el-icon><Plus /></el-icon> 添加选项
                </el-button>
              </div>
            </el-form-item>
          </template>

          <!-- Cascader options editor -->
          <template v-if="fields[selectedIndex].type === 'cascader'">
            <el-form-item label="级联数据（JSON）">
              <el-input
                v-model="fields[selectedIndex].cascaderOptionsJson"
                type="textarea"
                :rows="6"
                placeholder='[{"value":"zhejiang","label":"浙江","children":[...]}]'
                @blur="parseCascaderOptions(fields[selectedIndex])"
              />
            </el-form-item>
          </template>

          <!-- Tag default tags -->
          <template v-if="fields[selectedIndex].type === 'tag'">
            <el-form-item label="默认标签（逗号分隔）">
              <el-input
                v-model="fields[selectedIndex].defaultTagsStr"
                placeholder="标签1, 标签2, 标签3"
                @blur="parseTags(fields[selectedIndex])"
              />
            </el-form-item>
          </template>

          <!-- Number / Rate / Slider config -->
          <template v-if="['number', 'slider'].includes(fields[selectedIndex].type)">
            <el-row :gutter="8">
              <el-col :span="12">
                <el-form-item label="最小值">
                  <el-input-number v-model="fields[selectedIndex].min" style="width: 100%" size="small" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最大值">
                  <el-input-number v-model="fields[selectedIndex].max" style="width: 100%" size="small" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="步长" v-if="fields[selectedIndex].type === 'slider'">
              <el-input-number v-model="fields[selectedIndex].step" :min="0.1" style="width: 100%" size="small" />
            </el-form-item>
          </template>

          <el-form-item label="最大星数" v-if="fields[selectedIndex].type === 'rate'">
            <el-input-number v-model="fields[selectedIndex].max" :min="1" :max="10" style="width: 100%" size="small" />
          </el-form-item>

          <!-- Rows for textarea -->
          <el-form-item label="行数" v-if="fields[selectedIndex].type === 'textarea'">
            <el-input-number v-model="fields[selectedIndex].rows" :min="1" :max="10" size="small" />
          </el-form-item>

          <!-- Upload config -->
          <template v-if="fields[selectedIndex].type === 'upload'">
            <el-form-item label="上传地址">
              <el-input v-model="fields[selectedIndex].uploadUrl" placeholder="/api/upload" />
            </el-form-item>
            <el-form-item label="最大文件数">
              <el-input-number v-model="fields[selectedIndex].maxCount" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
            <el-form-item label="列表样式">
              <el-radio-group v-model="fields[selectedIndex].listType">
                <el-radio-button value="text">文件列表</el-radio-button>
                <el-radio-button value="picture">图片缩略</el-radio-button>
                <el-radio-button value="picture-card">卡片墙</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </template>

          <!-- Alert config -->
          <template v-if="fields[selectedIndex].type === 'alert'">
            <el-form-item label="提示类型">
              <el-radio-group v-model="fields[selectedIndex].alertType">
                <el-radio-button value="info">信息</el-radio-button>
                <el-radio-button value="success">成功</el-radio-button>
                <el-radio-button value="warning">警告</el-radio-button>
                <el-radio-button value="error">错误</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="提示内容">
              <el-input v-model="fields[selectedIndex].placeholder" placeholder="提示文案" />
            </el-form-item>
          </template>
        </el-form>
      </div>
    </div>

    <!-- ===== Preview Dialog ===== -->
    <el-dialog v-model="previewVisible" title="表单预览" width="760px" destroy-on-close>
      <SchemaFormRenderer :fields="fields" v-model="previewData" />
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="showPreviewData">查看数据</el-button>
      </template>
    </el-dialog>

    <!-- ===== Import Dialog ===== -->
    <el-dialog v-model="importVisible" title="导入JSON" width="600px">
      <el-input v-model="importJson" type="textarea" :rows="12" placeholder='[{"type":"input","label":"字段名","prop":"field1",...}]' />
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="doImport">导入</el-button>
      </template>
    </el-dialog>

    <!-- ===== Preview Data Dialog ===== -->
    <el-dialog v-model="dataVisible" title="表单数据" width="500px">
      <pre class="json-preview">{{ JSON.stringify(previewData, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, markRaw } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View, Download, Upload, Check, Plus, Delete, Rank, Top, Bottom,
  CopyDocument, Close, Document, EditPen, Calendar, Switch as SwitchIcon,
  Select, CircleCheck, Box, Lock, Timer, Picture, Files, Star,
  Discount, Histogram, UploadFilled, Sort, ChromeFilled,
  PriceTag, Minus, WarningFilled,
} from '@element-plus/icons-vue'
import { getFormConfigs, createFormConfig, updateFormConfig, deleteFormConfig } from '@/api/form_config'
import SchemaFormRenderer from '@/components/SchemaFormRenderer.vue'

// ==================== Field Type Groups ====================
const fieldGroups = [
  {
    title: '基础输入',
    items: [
      { type: 'input', label: '单行文本', icon: markRaw(EditPen) },
      { type: 'textarea', label: '多行文本', icon: markRaw(Document) },
      { type: 'password', label: '密码框', icon: markRaw(Lock) },
      { type: 'number', label: '数字', icon: markRaw(EditPen) },
      { type: 'tag', label: '标签输入', icon: markRaw(PriceTag) },
    ],
  },
  {
    title: '选择类',
    items: [
      { type: 'select', label: '下拉选择', icon: markRaw(Select) },
      { type: 'radio', label: '单选框组', icon: markRaw(CircleCheck) },
      { type: 'checkbox', label: '多选框组', icon: markRaw(Box) },
      { type: 'switch', label: '开关', icon: markRaw(SwitchIcon) },
      { type: 'cascader', label: '级联选择', icon: markRaw(Sort) },
      { type: 'transfer', label: '穿梭框', icon: markRaw(Files) },
    ],
  },
  {
    title: '日期时间',
    items: [
      { type: 'date', label: '日期', icon: markRaw(Calendar) },
      { type: 'datetime', label: '日期时间', icon: markRaw(Calendar) },
      { type: 'daterange', label: '日期范围', icon: markRaw(Calendar) },
      { type: 'time', label: '时间', icon: markRaw(Timer) },
    ],
  },
  {
    title: '高级组件',
    items: [
      { type: 'rate', label: '评分', icon: markRaw(Star) },
      { type: 'slider', label: '滑块', icon: markRaw(Discount) },
      { type: 'color', label: '颜色选择', icon: markRaw(ChromeFilled) },
      { type: 'upload', label: '文件上传', icon: markRaw(UploadFilled) },
    ],
  },
  {
    title: '布局展示',
    items: [
      { type: 'divider', label: '分割线', icon: markRaw(Minus) },
      { type: 'alert', label: '提示文字', icon: markRaw(WarningFilled) },
      { type: 'text', label: '纯文本', icon: markRaw(Document) },
    ],
  },
]

const allFieldTypes = fieldGroups.flatMap((g) => g.items)

function getTypeLabel(type) {
  const ft = allFieldTypes.find((f) => f.type === type)
  return ft ? ft.label : type
}

function isLayoutField(type) {
  return ['divider', 'alert', 'text'].includes(type)
}

function hasDefaultValue(type) {
  return !['cascader', 'transfer', 'upload', 'divider', 'alert', 'text'].includes(type)
}

// ==================== State ====================
const fields = ref([])
const selectedIndex = ref(-1)
const formName = ref('')
const formCode = ref('')
const formDesc = ref('')
const editingId = ref(null)
const saving = ref(false)
const savedForms = ref([])
const previewVisible = ref(false)
const previewData = ref({})
const importVisible = ref(false)
const importJson = ref('')
const dataVisible = ref(false)
const transferPreview = ref([])

let fieldIdCounter = 0

// ==================== Field Operations ====================
function addField(ft) {
  const newField = {
    id: ++fieldIdCounter,
    type: ft.type,
    label: ft.label,
    prop: `field_${fieldIdCounter}`,
    placeholder: '',
    defaultValue: '',
    required: false,
    span: 24,
    options: ['select', 'radio', 'checkbox', 'transfer'].includes(ft.type) ? [
      { label: '选项1', value: 'opt1' },
      { label: '选项2', value: 'opt2' },
    ] : [],
    min: 0,
    max: 100,
    step: 1,
    rows: 3,
    // type-specific defaults
    cascaderOptions: [],
    cascaderOptionsJson: '',
    defaultTags: [],
    defaultTagsStr: '',
    uploadUrl: '',
    maxCount: 5,
    listType: 'text',
    alertType: 'info',
  }
  fields.value.push(newField)
  selectedIndex.value = fields.value.length - 1
}

function selectField(index) {
  selectedIndex.value = index
}

function removeField(index) {
  fields.value.splice(index, 1)
  if (selectedIndex.value >= fields.value.length) {
    selectedIndex.value = fields.value.length - 1
  }
}

function moveUp(index) {
  if (index === 0) return
  const arr = fields.value
  ;[arr[index - 1], arr[index]] = [arr[index], arr[index - 1]]
  selectedIndex.value = index - 1
}

function moveDown(index) {
  if (index === fields.value.length - 1) return
  const arr = fields.value
  ;[arr[index], arr[index + 1]] = [arr[index + 1], arr[index]]
  selectedIndex.value = index + 1
}

function duplicateField(index) {
  const copy = JSON.parse(JSON.stringify(fields.value[index]))
  copy.id = ++fieldIdCounter
  copy.prop = `field_${fieldIdCounter}`
  fields.value.splice(index + 1, 0, copy)
  selectedIndex.value = index + 1
}

function clearFields() {
  fields.value = []
  selectedIndex.value = -1
}

function addOption(field) {
  const n = field.options.length + 1
  field.options.push({ label: `选项${n}`, value: `opt${n}` })
}

// ==================== Conditional Visibility Helpers ====================
function toggleVisibleWhen(field, enabled) {
  if (enabled) {
    field.visibleWhen = { prop: '', _op: 'equals', equals: '' }
  } else {
    delete field.visibleWhen
  }
}

function onVisibleWhenOpChange(field) {
  const op = field.visibleWhen._op
  // Clean up unused keys
  if (op === 'equals') {
    delete field.visibleWhen.notEquals
    delete field.visibleWhen.in
    delete field.visibleWhen._inStr
    if (field.visibleWhen.equals === undefined) field.visibleWhen.equals = ''
  } else if (op === 'notEquals') {
    delete field.visibleWhen.equals
    delete field.visibleWhen.in
    delete field.visibleWhen._inStr
    if (field.visibleWhen.notEquals === undefined) field.visibleWhen.notEquals = ''
  } else if (op === 'in') {
    delete field.visibleWhen.equals
    delete field.visibleWhen.notEquals
    if (field.visibleWhen._inStr === undefined) field.visibleWhen._inStr = ''
    if (field.visibleWhen.in === undefined) field.visibleWhen.in = []
  }
}

function parseVisibleWhenIn(field) {
  const str = field.visibleWhen._inStr || ''
  field.visibleWhen.in = str.split(',').map((s) => s.trim()).filter(Boolean)
}

function parseCascaderOptions(field) {
  try {
    field.cascaderOptions = JSON.parse(field.cascaderOptionsJson || '[]')
    ElMessage.success('级联数据已更新')
  } catch {
    ElMessage.error('JSON 格式错误')
  }
}

function parseTags(field) {
  field.defaultTags = (field.defaultTagsStr || '')
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
}

// ==================== Preview ====================
function handlePreview() {
  previewData.value = {}
  fields.value.forEach((f) => {
    if (isLayoutField(f.type)) return
    if (f.defaultValue !== '' && f.defaultValue !== undefined && f.defaultValue !== null) {
      previewData.value[f.prop] = f.type === 'number' || f.type === 'rate' || f.type === 'slider'
        ? Number(f.defaultValue)
        : f.defaultValue
    } else if (f.type === 'checkbox' || f.type === 'transfer') {
      previewData.value[f.prop] = []
    } else if (f.type === 'switch') {
      previewData.value[f.prop] = false
    } else if (f.type === 'tag') {
      previewData.value[f.prop] = [...(f.defaultTags || [])]
    } else {
      previewData.value[f.prop] = ''
    }
  })
  previewVisible.value = true
}

function showPreviewData() {
  dataVisible.value = true
}

// ==================== Import / Export ====================
function handleExport() {
  const json = JSON.stringify(fields.value, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${formCode.value || 'form'}_schema.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('JSON 已导出')
}

function handleImport() {
  importJson.value = ''
  importVisible.value = true
}

function doImport() {
  try {
    const parsed = JSON.parse(importJson.value)
    if (!Array.isArray(parsed)) throw new Error('JSON 应为数组格式')
    fields.value = parsed.map((f) => ({ ...f, id: ++fieldIdCounter }))
    importVisible.value = false
    ElMessage.success(`已导入 ${parsed.length} 个字段`)
  } catch (e) {
    ElMessage.error('JSON 格式错误: ' + e.message)
  }
}

// ==================== Save / Load ====================
async function handleSave() {
  if (!formName.value) {
    ElMessage.warning('请输入表单名称')
    return
  }
  if (!formCode.value) {
    ElMessage.warning('请输入表单编码')
    return
  }
  if (fields.value.length === 0) {
    ElMessage.warning('请至少添加一个字段')
    return
  }
  saving.value = true
  try {
    // Clean up internal helper fields before saving
    const cleanFields = fields.value.map((f) => {
      const clean = { ...f }
      if (clean.visibleWhen) {
        const vw = { ...clean.visibleWhen }
        delete vw._op
        delete vw._inStr
        clean.visibleWhen = vw
      }
      // Remove cascaderOptionsJson if it exists (keep only cascaderOptions)
      delete clean.cascaderOptionsJson
      delete clean.defaultTagsStr
      return clean
    })
    const payload = {
      name: formName.value,
      code: formCode.value,
      description: formDesc.value,
      form_schema: JSON.stringify(cleanFields),
      is_active: true,
    }
    if (editingId.value) {
      await updateFormConfig(editingId.value, payload)
      ElMessage.success('表单已更新')
    } else {
      const res = await createFormConfig(payload)
      editingId.value = res.id
      ElMessage.success('表单已创建')
    }
    fetchSavedForms()
  } finally {
    saving.value = false
  }
}

async function loadForm(item) {
  try {
    const schema = JSON.parse(item.form_schema)
    fields.value = schema.map((f) => {
      const field = { ...f, id: ++fieldIdCounter }
      // Restore _op helper for visibleWhen
      if (field.visibleWhen) {
        if (field.visibleWhen.equals !== undefined) field.visibleWhen._op = 'equals'
        else if (field.visibleWhen.notEquals !== undefined) field.visibleWhen._op = 'notEquals'
        else if (field.visibleWhen.in !== undefined) {
          field.visibleWhen._op = 'in'
          field.visibleWhen._inStr = (field.visibleWhen.in || []).join(',')
        }
      }
      return field
    })
    formName.value = item.name
    formCode.value = item.code
    formDesc.value = item.description || ''
    editingId.value = item.id
    selectedIndex.value = -1
    ElMessage.success(`已加载表单「${item.name}」`)
  } catch (e) {
    ElMessage.error('加载表单失败: ' + e.message)
  }
}

function newForm() {
  fields.value = []
  selectedIndex.value = -1
  formName.value = ''
  formCode.value = ''
  formDesc.value = ''
  editingId.value = null
}

async function handleDeleteSaved(item) {
  await ElMessageBox.confirm(`确定删除表单「${item.name}」？`, '删除确认', { type: 'warning' })
  await deleteFormConfig(item.id)
  ElMessage.success('已删除')
  if (editingId.value === item.id) newForm()
  fetchSavedForms()
}

async function fetchSavedForms() {
  try {
    const data = await getFormConfigs({ limit: 100 })
    savedForms.value = data.items
  } catch (e) {
    // ignore
  }
}

onMounted(fetchSavedForms)
</script>

<style scoped>
.designer-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  gap: 0;
}

/* ===== Toolbar ===== */
.designer-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px 8px 0 0;
  gap: 12px;
  flex-wrap: wrap;
}
.toolbar-left, .toolbar-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ===== Three Column Body ===== */
.designer-body {
  flex: 1;
  display: flex;
  gap: 1px;
  background: var(--el-border-color-lighter);
  border: 1px solid var(--el-border-color-light);
  border-top: none;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

/* ===== Panels ===== */
.palette-panel {
  flex: 0 0 200px;
  background: var(--el-bg-color);
  padding: 16px;
  overflow-y: auto;
}
.canvas-panel {
  flex: 1;
  background: var(--el-bg-color-page);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.property-panel {
  flex: 0 0 300px;
  background: var(--el-bg-color);
  padding: 16px;
  overflow-y: auto;
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ===== Palette Items ===== */
.palette-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.palette-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
  color: var(--el-text-color-regular);
}
.palette-item:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.palette-icon {
  font-size: 22px;
}

/* ===== Saved Forms List ===== */
.saved-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.saved-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}
.saved-item:hover {
  background: var(--el-fill-color-light);
}
.saved-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}
.saved-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== Canvas ===== */
.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
}
.canvas-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
.canvas-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--el-text-color-placeholder);
  gap: 12px;
}
.canvas-field {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: var(--el-bg-color);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.canvas-field:hover {
  border-color: var(--el-color-primary-light-5);
}
.canvas-field.selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
}
.canvas-field.is-layout {
  background: var(--el-fill-color-lighter);
}
.field-handle {
  color: var(--el-text-color-placeholder);
  cursor: grab;
  padding-top: 4px;
}
.field-content {
  flex: 1;
}
.field-actions {
  display: flex;
  flex-direction: column;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
}
.canvas-field:hover .field-actions,
.canvas-field.selected .field-actions {
  opacity: 1;
}

/* ===== Property Panel ===== */
.empty-hint {
  color: var(--el-text-color-placeholder);
  font-size: 13px;
  text-align: center;
  padding: 20px 0;
}

/* ===== Options Editor ===== */
.options-editor {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}
.option-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ===== Conditional Visibility Config ===== */
.visible-when-config {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}
.vw-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.vw-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

/* ===== Tag Preview ===== */
.tag-preview {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* ===== Text Display ===== */
.text-display {
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.6;
}

/* ===== JSON Preview ===== */
.json-preview {
  background: var(--el-fill-color-dark);
  color: #e0e0e0;
  padding: 16px;
  border-radius: 8px;
  font-size: 13px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}
</style>
