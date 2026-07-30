<template>
  <CrudTablePage
    :api="api"
    form-config-code="license_form"
    :default-schema="defaultSchema"
    :core-fields="coreFields"
    :columns="columns"
    :default-visible-columns="defaultVisibleColumns"
    title="授权管理"
    entity-name="授权"
    name-field="device_name"
    search-placeholder="品牌/设备名称/设备类型"
    storage-key="license_columns"
  />
</template>

<script setup>
import CrudTablePage from '@/components/CrudTablePage.vue'
import {
  getLicenses, getLicense,
  createLicense, updateLicense, deleteLicense,
} from '@/api/license'
import { DEVICE_CATEGORY_TREE, DEVICE_TYPE_LABEL_MAP } from '@/constants/vendors'

// 设备类型扁平选项（用于授权列表/详情中 device_type 代码 → 中文标签）
const FLAT_DEVICE_TYPE_OPTIONS = DEVICE_CATEGORY_TREE.reduce((acc, cat) => {
  cat.options.forEach((o) => acc.push({ label: o.label, value: o.value }))
  return acc
}, [])

const api = {
  list: getLicenses, get: getLicense,
  create: createLicense, update: updateLicense, delete: deleteLicense,
}

const coreFields = [
  'brand', 'device_type', 'asset_id', 'device_name',
  'license_key', 'activation_date', 'expiration_date', 'status', 'remark',
]

// 设备类型下拉（与资产统计分类一致，三大类 24 种）
const deviceTypeOptions = DEVICE_CATEGORY_TREE

const defaultSchema = [
  { type: 'divider', label: '授权信息', span: 24 },
  {
    type: 'select-icon', label: '品牌', prop: 'brand', span: 12, options: [
      { label: '华为', value: '华为', icon: '/brand-icons/huawei.png' },
      { label: '深信服', value: '深信服', icon: '/brand-icons/sangfor.png' },
      { label: '绿盟', value: '绿盟', icon: '/brand-icons/nsfocus.png' },
      { label: 'H3C', value: 'H3C', icon: '/brand-icons/h3c.png' },
      { label: '信锐', value: '信锐', emoji: '📡' },
    ],
  },
  {
    // 设备类型：两级联动（先选大类，再选具体类型）
    type: 'select-cascade', label: '设备类型', prop: 'device_type', span: 12,
    cascaderOptions: deviceTypeOptions,
  },
  {
    // 设备名称：先选设备类型过滤，再从已过滤的资产中选择（避免设备过多下拉太长）
    type: 'select-remote-filtered', label: '设备名称', prop: 'device_name', span: 12,
    placeholder: '先选上方设备类型，再选设备', remoteUrl: '/assets', remoteLabelKey: 'device_name', remoteValueKey: 'device_name',
    filterProp: 'device_type', // 关联本表单的 device_type 字段进行过滤
  },
  { type: 'input', label: '授权码', prop: 'license_key', span: 12, placeholder: '授权码/序列号' },
  { type: 'date', label: '激活日期', prop: 'activation_date', span: 12 },
  { type: 'date', label: '到期日期', prop: 'expiration_date', span: 12 },
  {
    type: 'select', label: '状态', prop: 'status', span: 12, disabled: true, options: [
      { label: '正常', value: '正常' }, { label: '临期2月', value: '临期2月' },
      { label: '临期1月', value: '临期1月' }, { label: '临期15天', value: '临期15天' },
      { label: '过期', value: '过期' },
    ],
  },
  { type: 'textarea', label: '备注', prop: 'remark', span: 24, rows: 2 },
]

// 品牌图标的图像/emoji 映射（表格与详情显示）
const brandIconMap = {
  '华为': '/brand-icons/huawei.png',
  '深信服': '/brand-icons/sangfor.png',
  '绿盟': '/brand-icons/nsfocus.png',
  'H3C': '/brand-icons/h3c.png',
}
const brandEmojiMap = { '信锐': '📡' }

// 授权状态彩色映射
const statusColorMap = {
  '正常': '#67C23A',
  '临期2月': '#409EFF',
  '临期1月': '#E6A23C',
  '临期15天': '#FF8C00',
  '过期': '#F56C6C',
}

const columns = [
  { prop: 'brand', label: '品牌', width: 120, type: 'icon', iconMap: brandIconMap, emojiMap: brandEmojiMap },
  { prop: 'device_type', label: '设备类型', width: 120, options: FLAT_DEVICE_TYPE_OPTIONS },
  { prop: 'device_name', label: '设备名称', minWidth: 120 },
  { prop: 'license_key', label: '授权码', minWidth: 150 },
  { prop: 'activation_date', label: '激活日期', width: 120, type: 'date' },
  { prop: 'expiration_date', label: '到期日期', width: 120, type: 'date' },
  { prop: 'status', label: '状态', width: 110, type: 'tag', colorMap: statusColorMap },
]

const defaultVisibleColumns = ['id', 'brand', 'device_type', 'device_name', 'activation_date', 'expiration_date', 'status']
</script>
