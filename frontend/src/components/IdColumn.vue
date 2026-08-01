<template>
  <!-- 全项目统一的 ID 列封装：prop/label/width/sortable 单一来源，修改此处即同步所有页面 -->
  <el-table-column
    v-if="visible"
    prop="id"
    label="ID"
    :width="width"
    :sortable="sortable ? 'custom' : false"
  />
</template>

<script setup>
// 统一 ID 列：默认 width=70（足够容纳 "ID" 字样 + Element Plus 排序箭头，避免 ellipsis 截断出现 "..." 占位）
// - sortable: 是否允许点击列头正/倒序。后端需支持 order 参数的页面才传 true（默认）。
// - visible:  是否渲染该列，用于 statistics 等带“列可见性”开关的页面。
defineProps({
  width: { type: [Number, String], default: 70 },
  sortable: { type: Boolean, default: true },
  visible: { type: Boolean, default: true },
})
</script>
