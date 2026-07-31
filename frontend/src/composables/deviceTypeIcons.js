import { reactive } from 'vue'

/**
 * 设备类型图标「运行时覆盖」映射。
 *
 * 背景：字段管理（系统管理 → 字段管理）允许为每个 device_type 选项单独配置图标
 * （写入 system_field.icon）。但统计页/端口互联页的 <DeviceTypeIcon> 原本只从
 * vendors.js 的静态 DEVICE_TYPE_ICON 读 emoji/themeColor，导致在字段管理里配的图标
 * 在列表/详情/预览里完全不生效。
 *
 * 这里用一个全局 reactive 映射 value(设备类型) -> 图标路径，统计页加载表单 schema
 * 后调用 buildDeviceTypeIconMap() 填充，<DeviceTypeIcon> 渲染时优先使用，从而让
 * 「图标库上传 → 字段管理选图标」的配置真正在页面上生效（无需改 vendors.js）。
 */
export const deviceTypeIconOverrides = reactive({})

function walk(list) {
  for (const o of list || []) {
    if (o && o.value && o.icon) {
      deviceTypeIconOverrides[o.value] = o.icon
    }
    if (o.options && o.options.length) walk(o.options)
    if (o.children && o.children.length) walk(o.children)
  }
}

/**
 * 从 device_type 字段的选项（两级树或扁平）中提取 value→icon 映射并写入全局覆盖表。
 * 选项结构（来自 getFieldOptions('device_type')）：
 *   [{ label:'网络设备类', options:[{ label:'交换机', value:'switch', icon?, emoji? }, ...] }, ...]
 * 兼容扁平结构 [{ value, icon }] 与 children 嵌套。
 */
export function buildDeviceTypeIconMap(options) {
  walk(options)
}

export function clearDeviceTypeIconOverrides() {
  Object.keys(deviceTypeIconOverrides).forEach((k) => {
    delete deviceTypeIconOverrides[k]
  })
}
