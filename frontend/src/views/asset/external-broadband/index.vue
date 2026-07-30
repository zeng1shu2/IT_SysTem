<template>
  <CrudTablePage
    :api="api"
    form-config-code="external_broadband_form"
    :default-schema="defaultSchema"
    :core-fields="coreFields"
    :columns="columns"
    :default-visible-columns="defaultVisibleColumns"
    title="IPS带宽"
    entity-name="IPS带宽"
    name-field="operator"
    search-placeholder="运营商/线路类型/IP/归属"
    storage-key="external_broadband_columns"
  />
</template>

<script setup>
import CrudTablePage from '@/components/CrudTablePage.vue'
import {
  getExternalBroadbands, getExternalBroadband,
  createExternalBroadband, updateExternalBroadband, deleteExternalBroadband,
} from '@/api/external-broadband'

const api = {
  list: getExternalBroadbands, get: getExternalBroadband,
  create: createExternalBroadband, update: updateExternalBroadband, delete: deleteExternalBroadband,
}

const coreFields = [
  'operator', 'line_type', 'status', 'ip_address', 'mask', 'gateway',
  'dial_account', 'vlan', 'bandwidth', 'ownership', 'remark',
]

// 运营商图标映射（与表单种子一致）
const operatorIconMap = {
  电信: '/brand-icons/telecom.png',
  联通: '/brand-icons/unicom.png',
  移动: '/brand-icons/mobile.png',
  广电: '/brand-icons/broadcast.png',
}
const operatorEmojiMap = { 其他: '🌐' }

// 状态颜色映射
const statusColorMap = {
  正常: '#67C23A',
  空闲: '#409EFF',
  故障: '#E6A23C',
  停用: '#F56C6C',
}

const defaultSchema = [
  { type: 'divider', label: '线路信息', span: 24 },
  {
    type: 'select-icon', label: '运营商', prop: 'operator', span: 12,
    options: [
      { label: '中国电信', value: '电信', icon: '/brand-icons/telecom.png' },
      { label: '中国联通', value: '联通', icon: '/brand-icons/unicom.png' },
      { label: '中国移动', value: '移动', icon: '/brand-icons/mobile.png' },
      { label: '中国广电', value: '广电', icon: '/brand-icons/broadcast.png' },
      { label: '其他', value: '其他', emoji: '🌐' },
    ],
  },
  {
    type: 'select', label: '线路类型', prop: 'line_type', span: 12,
    options: [
      { label: '专线', value: '专线' },
      { label: '宽带', value: '宽带' },
      { label: '光纤', value: '光纤' },
      { label: '其他', value: '其他' },
    ],
  },
  {
    type: 'select', label: '状态', prop: 'status', span: 12, defaultValue: '正常',
    options: [
      { label: '正常', value: '正常' },
      { label: '空闲', value: '空闲' },
      { label: '故障', value: '故障' },
      { label: '停用', value: '停用' },
    ],
  },
  { type: 'input', label: 'IP', prop: 'ip_address', span: 12, placeholder: '如：202.96.128.86' },
  { type: 'input', label: '掩码', prop: 'mask', span: 12, placeholder: '如：255.255.255.252' },
  { type: 'input', label: '网关', prop: 'gateway', span: 12, placeholder: '如：202.96.128.85' },
  { type: 'input', label: '拨号账号/接入号', prop: 'dial_account', span: 12, placeholder: '拨号账号或接入号' },
  { type: 'input', label: '对应VLAN', prop: 'vlan', span: 12, placeholder: '如：VLAN 100' },
  { type: 'input', label: '线路带宽', prop: 'bandwidth', span: 12, placeholder: '如：100M' },
  { type: 'input', label: '线路归属', prop: 'ownership', span: 12, placeholder: '如：总部/分公司A' },
  { type: 'textarea', label: '备注', prop: 'remark', span: 24, rows: 2 },
]

const columns = [
  { prop: 'operator', label: '运营商', width: 130, type: 'icon', iconMap: operatorIconMap, emojiMap: operatorEmojiMap },
  { prop: 'line_type', label: '线路类型', width: 100 },
  { prop: 'status', label: '状态', width: 90, type: 'tag', colorMap: statusColorMap },
  { prop: 'ip_address', label: 'IP', width: 140 },
  { prop: 'mask', label: '掩码', width: 140 },
  { prop: 'gateway', label: '网关', width: 140 },
  { prop: 'dial_account', label: '拨号账号', minWidth: 120 },
  { prop: 'vlan', label: 'VLAN', width: 100 },
  { prop: 'bandwidth', label: '带宽', width: 100 },
  { prop: 'ownership', label: '线路归属', minWidth: 120 },
]

const defaultVisibleColumns = ['id', 'operator', 'line_type', 'status', 'ip_address', 'vlan', 'bandwidth', 'ownership']
</script>
