<template>
  <div class="port-groups-editor">
    <el-table v-if="local.length > 0" :data="local" border size="small">
      <el-table-column label="接口类型" min-width="170">
        <template #default="{ row }">
          <el-select v-model="row.type" size="small" style="width: 100%" @change="onRowChange">
            <el-option v-for="t in PORT_TYPES" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="端口数" width="140">
        <template #default="{ row }">
          <el-input-number
            v-model="row.count"
            :min="0"
            :max="9999"
            size="small"
            style="width: 100%"
            controls-position="right"
            @change="onRowChange"
          />
        </template>
      </el-table-column>
      <el-table-column label="端口命名预览" min-width="230">
        <template #default="{ row }">
          <span class="pg-preview">{{ previewGroupRange(row) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="70" fixed="right">
        <template #default="{ $index }">
          <el-button size="small" type="danger" link @click="removeRow($index)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div v-else class="pg-empty">暂无端口组，点击下方按钮添加端口类型</div>

    <div class="pg-actions">
      <el-button size="small" type="primary" plain @click="addRow">
        <el-icon><Plus /></el-icon> 添加端口组
      </el-button>
      <span class="pg-total">共 {{ totalCount }} 个物理端口</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { PORT_TYPES, previewGroupRange, totalPortCount } from '@/utils/portNaming'

const props = defineProps({
  modelValue: { type: [Array, Object], default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const local = ref(Array.isArray(props.modelValue) ? props.modelValue : [])

watch(
  () => props.modelValue,
  (v) => {
    if (v !== local.value) local.value = Array.isArray(v) ? v : []
  },
)

const totalCount = computed(() => totalPortCount(local.value))

function sync() {
  emit('update:modelValue', local.value)
}

function addRow() {
  local.value.push({ type: 'ge_elec', count: 1 })
  sync()
}

function removeRow(index) {
  local.value.splice(index, 1)
  sync()
}

function onRowChange() {
  sync()
}
</script>

<style scoped>
.port-groups-editor { width: 100%; }
.pg-empty {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  padding: 14px 0;
  text-align: center;
  border: 1px dashed var(--el-border-color);
  border-radius: 4px;
  margin-bottom: 10px;
}
.pg-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 10px;
}
.pg-total { font-size: 13px; color: var(--el-text-color-secondary); }
.pg-preview { font-family: monospace; font-size: 13px; color: var(--el-color-primary); }
</style>
