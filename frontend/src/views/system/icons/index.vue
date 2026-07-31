<template>
  <div class="page-container icons-page">
    <!-- 顶部工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="keyword"
            placeholder="搜索图标名称"
            clearable
            style="width: 240px"
            @input="reload"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="category" placeholder="全部分类" clearable style="width: 160px" @change="reload">
            <el-option v-for="c in ICON_CATEGORIES" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
          <el-checkbox v-model="includeInactive" @change="reload">包含已禁用</el-checkbox>
        </div>
        <div class="toolbar-right">
          <span class="text-muted">共 {{ total }} 个图标</span>
          <el-upload
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="onUpload"
            accept="image/png,image/jpeg,image/svg+xml,image/webp,image/gif"
          >
            <el-button type="primary" :loading="uploading">
              <el-icon><Upload /></el-icon> 上传图标
            </el-button>
          </el-upload>
        </div>
      </div>
    </el-card>

    <!-- 图标网格 -->
    <el-card shadow="never" class="grid-card">
      <div v-if="loading && items.length === 0" class="empty-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="items.length === 0" class="empty-state">
        <el-empty description="暂无图标，点击右上角「上传图标」添加" />
      </div>
      <div v-else class="icon-grid">
        <div
          v-for="icon in items"
          :key="icon.id"
          class="icon-tile"
          :class="{ disabled: !icon.is_active }"
          @click="copyPath(icon)"
          @contextmenu.prevent
        >
          <div class="icon-preview">
            <img v-if="icon.mime !== 'image/svg+xml'" :src="icon.path" :alt="icon.name" />
            <object v-else :data="icon.path" type="image/svg+xml" class="svg-object" />
            <el-tag v-if="!icon.is_active" size="small" type="info" class="status-tag">已禁用</el-tag>
          </div>
          <div class="icon-meta">
            <div class="icon-name" :title="icon.name">{{ icon.name }}</div>
            <div class="icon-sub">
              <el-tag size="small" effect="plain" type="info">{{ categoryLabel(icon.category) }}</el-tag>
              <span class="icon-size">{{ formatSize(icon.size) }}</span>
            </div>
          </div>
          <div class="icon-actions">
            <el-button size="small" link type="primary" @click.stop="copyPath(icon)">复制路径</el-button>
            <el-button
              v-if="userStore.isAdmin && icon.is_active"
              size="small"
              link
              type="danger"
              @click.stop="handleDelete(icon)"
            >
              禁用
            </el-button>
            <el-button
              v-if="userStore.isAdmin"
              size="small"
              link
              type="danger"
              @click.stop="handlePermanentDelete(icon)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { listIcons, uploadIcon, deleteIcon, permanentDeleteIcon, ICON_CATEGORIES } from '@/api/icon'

const userStore = useUserStore()

const items = ref([])
const total = ref(0)
const loading = ref(false)
const uploading = ref(false)
const keyword = ref('')
const category = ref('')
const includeInactive = ref(false)

async function reload() {
  loading.value = true
  try {
    const res = await listIcons({
      keyword: keyword.value || undefined,
      category: category.value || undefined,
      include_inactive: includeInactive.value ? 'true' : undefined,
    })
    items.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    ElMessage.error('加载图标失败: ' + (err?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function beforeUpload(file) {
  const max = 2 * 1024 * 1024
  if (file.size > max) {
    ElMessage.error('文件超过 2MB 限制')
    return false
  }
  return true
}

async function onUpload(option) {
  const file = option.file
  uploading.value = true
  try {
    await uploadIcon({
      file,
      name: file.name.replace(/\.[^.]+$/, ''),
      category: category.value || 'other',
    })
    ElMessage.success('上传成功')
    reload()
  } catch (err) {
    const detail = err?.response?.data?.detail
    ElMessage.error('上传失败: ' + (typeof detail === 'string' ? detail : err?.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

async function handleDelete(icon) {
  try {
    await ElMessageBox.confirm(
      `确定禁用图标「${icon.name}」？禁用后字段选项中不会再列出（数据库记录与磁盘文件保留）。`,
      '禁用图标',
      { type: 'warning' },
    )
  } catch {
    return
  }
  try {
    await deleteIcon(icon.id)
    ElMessage.success('已禁用')
    reload()
  } catch (err) {
    ElMessage.error('禁用失败: ' + (err?.message || '未知错误'))
  }
}

async function handlePermanentDelete(icon) {
  try {
    await ElMessageBox.confirm(
      `确定永久删除图标「${icon.name}」？此操作不可恢复（数据库记录与磁盘文件都会删除）。`,
      '永久删除图标',
      { type: 'warning', confirmButtonText: '永久删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await permanentDeleteIcon(icon.id)
    ElMessage.success('已永久删除')
    reload()
  } catch (err) {
    ElMessage.error('删除失败: ' + (err?.message || '未知错误'))
  }
}

async function copyPath(icon) {
  try {
    await navigator.clipboard.writeText(icon.path)
    ElMessage.success(`已复制路径: ${icon.path}`)
  } catch {
    ElMessage.info(`路径: ${icon.path}`)
  }
}

function categoryLabel(val) {
  return ICON_CATEGORIES.find((c) => c.value === val)?.label || val || '其他'
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

onMounted(reload)
</script>

<style scoped>
.icons-page {
  height: 100%;
}

.toolbar-card {
  flex-shrink: 0;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.grid-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.grid-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 16px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  flex: 1;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 16px;
}

.icon-tile {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px;
  background: var(--el-bg-color);
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.icon-tile:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}
.icon-tile.disabled {
  opacity: 0.5;
  background: var(--el-fill-color-light);
}

.icon-preview {
  position: relative;
  width: 100%;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-blank);
  border-radius: 6px;
  overflow: hidden;
}
.icon-preview img,
.icon-preview .svg-object {
  max-width: 80%;
  max-height: 80%;
  object-fit: contain;
}
.status-tag {
  position: absolute;
  top: 4px;
  right: 4px;
}

.icon-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 0;
}
.icon-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.icon-sub {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.icon-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  border-top: 1px dashed var(--el-border-color-lighter);
  padding-top: 8px;
}

.text-muted {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>