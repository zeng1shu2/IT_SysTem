<template>
  <div class="field-mgmt">
    <el-row :gutter="16">
      <!-- Left: field groups -->
      <el-col :span="5">
        <el-card shadow="never" class="group-card">
          <template #header><span class="card-title">受管字段</span></template>
          <el-menu :default-active="currentGroup" @select="onSelect" class="group-menu">
            <el-menu-item v-for="g in groups" :key="g.code" :index="g.code">
              <el-icon><Collection /></el-icon>
              <span>{{ g.name }}</span>
              <el-tag v-if="g.type === 'tree'" size="small" type="info" effect="plain" class="group-tag">两级</el-tag>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- Right: options of the selected group -->
      <el-col :span="19">
        <el-card shadow="never">
          <template #header>
            <div class="header-bar">
              <span class="card-title">{{ groupMeta.name }} · 选项管理</span>
              <el-button v-if="isTree" type="primary" size="small" @click="openAddCategory">
                <el-icon><Plus /></el-icon> 新增大类
              </el-button>
              <el-button v-else type="primary" size="small" @click="openAddFlat">
                <el-icon><Plus /></el-icon> 新增选项
              </el-button>
            </div>
          </template>

          <el-alert
            type="success" :closable="false" show-icon class="hint"
            title="集中管理后自动同步"
            description="这里的选项会被资产统计、授权管理、IPS带宽等所有相关表单自动加载，新增/修改后无需改代码即生效。"
          />

          <el-table
            :data="tableData" row-key="id" :tree-props="{ children: 'children' }"
            :load="() => {}" lazy v-loading="loading" border stripe style="width: 100%; margin-top: 12px"
          >
            <el-table-column prop="label" label="显示名" min-width="140" />
            <el-table-column prop="value" label="选项值" min-width="140" />
            <el-table-column v-if="isTree" label="层级" width="90">
              <template #default="{ row }">{{ row.level === 0 ? '大类' : '小类' }}</template>
            </el-table-column>
            <el-table-column label="图标" width="90">
              <template #default="{ row }">
                <img v-if="row.icon" :src="row.icon" class="opt-icon" alt="" />
                <span v-else-if="row.emoji" class="opt-emoji">{{ row.emoji }}</span>
                <span v-else class="text-muted">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="sort" label="排序" width="80" />
            <el-table-column label="启用" width="90">
              <template #default="{ row }">
                <el-switch
                  :model-value="row.is_active === 1"
                  @change="(v) => { row.is_active = v ? 1 : 0; toggleActive(row) }"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" :min-width="colWidth('operation')" fixed="right">
              <template #default="{ row }">
                <el-button v-if="isTree && row.level === 0" size="small" link type="primary" @click="openAddSubtype(row)">添加小类</el-button>
                <el-button size="small" link @click="openEdit(row)">编辑</el-button>
                <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && tableData.length === 0" :description="`${groupMeta.name} 暂无选项，点击右上角新增`" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Add / Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="460px" @close="resetForm">
      <el-form :model="form" label-width="90px">
        <el-form-item label="显示名" required>
          <el-input v-model="form.label" placeholder="如：交换机 / 华为 / 北京总部" />
        </el-form-item>
        <el-form-item label="选项值" required>
          <el-input v-model="form.value" placeholder="存储值，如 switch / 华为 / BJ" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item v-if="isTree && form.level === 1" label="所属大类">
          <el-input :model-value="form.parent_value" disabled />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="图标">
          <div class="icon-picker-row">
            <div class="icon-preview-box">
              <img v-if="form.icon" :src="form.icon" alt="" />
              <span v-else-if="form.emoji" class="opt-emoji">{{ form.emoji }}</span>
              <span v-else class="text-muted">—</span>
            </div>
            <el-input v-model="form.icon" placeholder="/icons/... 或其他路径" style="flex: 1" />
            <el-button @click="openIconPicker">
              <el-icon><Picture /></el-icon> 从图标库选
            </el-button>
            <el-button v-if="form.icon" link type="danger" @click="form.icon = ''">清除</el-button>
          </div>
        </el-form-item>
        <el-form-item label="Emoji">
          <el-input v-model="form.emoji" placeholder="如 📡（与图标路径二选一）" maxlength="4" style="width: 160px" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Icon picker dialog (从图标库选图标) -->
    <el-dialog v-model="iconPickerVisible" title="从图标库选择" width="720px" @open="loadIconLibrary">
      <div class="picker-toolbar">
        <el-input v-model="pickerKeyword" placeholder="搜索图标" clearable style="width: 200px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="pickerCategory" placeholder="全部分类" clearable style="width: 140px">
          <el-option v-for="c in ICON_CATEGORIES" :key="c.value" :label="c.label" :value="c.value" />
        </el-select>
      </div>
      <div v-if="pickerItems.length === 0" class="picker-empty">
        <el-empty description="图标库为空，请先到「系统管理 → 图标管理」上传" />
      </div>
      <div v-else class="picker-grid">
        <div
          v-for="icon in pickerItems"
          :key="icon.id"
          class="picker-tile"
          :class="{ selected: form.icon === icon.path }"
          @click="pickIcon(icon)"
        >
          <img :src="icon.path" :alt="icon.name" />
          <span class="picker-name">{{ icon.name }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Collection, Search, Picture } from '@element-plus/icons-vue'
import {
  FIELD_GROUPS, listSystemFields, createSystemField, updateSystemField, deleteSystemField,
} from '@/api/system-field'
import { listIcons, ICON_CATEGORIES } from '@/api/icon'
import { colWidth } from '@/constants/columnWidths'

const groups = FIELD_GROUPS
const currentGroup = ref(FIELD_GROUPS[0].code)
const groupMeta = computed(() => groups.find((g) => g.code === currentGroup.value))
const isTree = computed(() => groupMeta.value.type === 'tree')

const loading = ref(false)
const tableData = ref([])

async function loadGroup() {
  loading.value = true
  try {
    const res = await listSystemFields(currentGroup.value)
    const items = res.items || []
    if (isTree.value) {
      const cats = items.filter((r) => r.level === 0)
      const subs = items.filter((r) => r.level === 1)
      tableData.value = cats.map((c) => ({ ...c, children: subs.filter((s) => s.parent_value === c.value) }))
    } else {
      tableData.value = items
    }
  } finally {
    loading.value = false
  }
}

function onSelect(code) {
  currentGroup.value = code
  loadGroup()
}

// ===== Dialog =====
const dialogVisible = ref(false)
const editingId = ref(null)
const saving = ref(false)
const dialogMode = ref('flat')
const form = reactive({
  field_code: '', field_name: '', value: '', label: '', icon: '', emoji: '',
  sort: 0, is_active: 1, parent_value: null, level: 0,
})

const dialogTitle = computed(() => {
  if (editingId.value) return `编辑${groupMeta.value.name}选项`
  if (dialogMode.value === 'category') return `新增大类（${groupMeta.value.name}）`
  if (dialogMode.value === 'subtype') return `新增小类（${groupMeta.value.name}）`
  return `新增${groupMeta.value.name}选项`
})

function resetForm() {
  Object.assign(form, {
    field_code: '', field_name: '', value: '', label: '', icon: '', emoji: '',
    sort: 0, is_active: 1, parent_value: null, level: 0,
  })
  editingId.value = null
}

function openAddFlat() {
  resetForm()
  dialogMode.value = 'flat'
  form.field_code = currentGroup.value
  form.field_name = groupMeta.value.name
  dialogVisible.value = true
}

function openAddCategory() {
  resetForm()
  dialogMode.value = 'category'
  form.field_code = 'device_type'
  form.field_name = '设备类型'
  form.level = 0
  form.parent_value = null
  dialogVisible.value = true
}

function openAddSubtype(row) {
  resetForm()
  dialogMode.value = 'subtype'
  form.field_code = 'device_type'
  form.field_name = '设备类型'
  form.level = 1
  form.parent_value = row.value
  dialogVisible.value = true
}

function openEdit(row) {
  resetForm()
  editingId.value = row.id
  dialogMode.value = row.level === 0 ? 'category' : 'flat'
  form.field_code = row.field_code
  form.field_name = row.field_name
  form.value = row.value
  form.label = row.label
  form.icon = row.icon || ''
  form.emoji = row.emoji || ''
  form.sort = row.sort || 0
  form.is_active = row.is_active
  form.parent_value = row.parent_value
  form.level = row.level
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.label || !form.value) {
    ElMessage.warning('请填写显示名与选项值')
    return
  }
  saving.value = true
  const payload = { ...form }
  try {
    if (editingId.value) {
      await updateSystemField(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createSystemField(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadGroup()
  } catch (err) {
    const d = err?.response?.data?.detail
    ElMessage.error('操作失败: ' + (typeof d === 'string' ? d : (err?.message || '未知错误')))
  } finally {
    saving.value = false
  }
}

async function toggleActive(row) {
  try {
    await updateSystemField(row.id, { is_active: row.is_active })
  } catch {
    loadGroup()
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除「${row.label}」吗？删除后相关表单将不再显示该选项。`, '删除确认', { type: 'warning' })
  await deleteSystemField(row.id)
  ElMessage.success('删除成功')
  loadGroup()
}

// ===== Icon picker =====
const iconPickerVisible = ref(false)
const pickerKeyword = ref('')
const pickerCategory = ref('')
const pickerItems = ref([])

async function loadIconLibrary() {
  try {
    const res = await listIcons({
      keyword: pickerKeyword.value || undefined,
      category: pickerCategory.value || undefined,
    })
    pickerItems.value = res.items || []
  } catch (err) {
    ElMessage.error('加载图标库失败: ' + (err?.message || '未知错误'))
    pickerItems.value = []
  }
}

function openIconPicker() {
  iconPickerVisible.value = true
}

function pickIcon(icon) {
  form.icon = icon.path
  iconPickerVisible.value = false
  ElMessage.success(`已选择: ${icon.name}`)
}

onMounted(loadGroup)
</script>

<style scoped>
.field-mgmt { padding: 4px; }
.group-card { height: 100%; }
.group-menu { border-right: none; }
.group-tag { margin-left: 8px; }
.card-title { font-weight: 600; font-size: 15px; }
.header-bar { display: flex; justify-content: space-between; align-items: center; }
.hint { margin-bottom: 12px; }
.opt-icon { width: 22px; height: 22px; object-fit: contain; border-radius: 4px; }
.opt-emoji { font-size: 18px; }
.text-muted { color: var(--el-text-color-secondary); }

/* Icon picker row inside the form */
.icon-picker-row {
  display: flex;
  gap: 8px;
  align-items: center;
  width: 100%;
}
.icon-preview-box {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}
.icon-preview-box img {
  max-width: 80%;
  max-height: 80%;
  object-fit: contain;
}

/* Icon picker dialog */
.picker-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.picker-empty {
  padding: 20px 0;
}
.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 12px;
  max-height: 420px;
  overflow-y: auto;
  padding: 4px;
}
.picker-tile {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--el-bg-color);
}
.picker-tile:hover {
  border-color: var(--el-color-primary);
  transform: translateY(-2px);
}
.picker-tile.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.picker-tile img {
  width: 48px;
  height: 48px;
  object-fit: contain;
}
.picker-name {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
</style>
