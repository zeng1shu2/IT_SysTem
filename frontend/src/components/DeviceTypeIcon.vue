<template>
  <!--
    设备类型图标渲染：三层优先级
      1. icon 路径（用户在图标库上传后，会在 vendors.js 配置 PNG/SVG）
      2. emoji 字符
      3. themeColor 主题色块（最底兜底）
    三种尺寸：small（行内 28px）/ medium（快速预览 52px）/ large（详情 hero 60px+）
  -->
  <span
    class="device-icon"
    :class="['size-' + size]"
    :style="{ background: icon.icon ? '#f5f7fa' : (icon.themeColor || '#c0c4cc') }"
  >
    <img v-if="icon.icon" :src="icon.icon" :alt="val" />
    <span v-else-if="icon.emoji" class="emoji">{{ icon.emoji }}</span>
    <span v-else class="emoji">❔</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { getDeviceTypeIcon } from '@/constants/vendors'
import { deviceTypeIconOverrides } from '@/composables/deviceTypeIcons'

const props = defineProps({
  val: { type: String, default: '' },
  icon: { type: String, default: '' },
  size: {
    type: String,
    default: 'small',
    validator: (v) => ['small', 'medium', 'large'].includes(v),
  },
})

const icon = computed(() => {
  const base = getDeviceTypeIcon(props.val)
  const override = props.icon || deviceTypeIconOverrides[props.val]
  if (override) return { icon: override, themeColor: base.themeColor }
  return base
})
</script>

<style scoped>
.device-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: #fff;
  flex-shrink: 0;
  overflow: hidden;
  vertical-align: middle;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
.device-icon img {
  width: 76%;
  height: 76%;
  object-fit: contain;
  /* 显示上传图标的原色，不再强制白色滤镜（避免彩色厂商图标被洗白） */
}
.emoji {
  line-height: 1;
  font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
}

/* Sizes */
.size-small {
  width: 28px;
  height: 28px;
  font-size: 16px;
  border-radius: 6px;
}
.size-medium {
  width: 52px;
  height: 52px;
  font-size: 26px;
  border-radius: 12px;
}
.size-large {
  width: 64px;
  height: 64px;
  font-size: 30px;
  border-radius: 14px;
}
</style>