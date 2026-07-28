<template>
  <CrudTablePage
    :api="api"
    form-config-code="external_broadband_form"
    :default-schema="defaultSchema"
    :core-fields="coreFields"
    :columns="columns"
    :default-visible-columns="defaultVisibleColumns"
    title="外线宽带"
    entity-name="外线宽带"
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
  'operator', 'line_type', 'ip_address', 'mask', 'gateway',
  'dial_account', 'vlan', 'bandwidth', 'ownership', 'remark',
]

const defaultSchema = [
  { type: 'divider', label: '线路信息', span: 24 },
  {
    type: 'select', label: '运营商', prop: 'operator', span: 12,
    options: [
      { label: '中国电信', value: '电信' },
      { label: '中国联通', value: '联通' },
      { label: '中国移动', value: '移动' },
      { label: '其他', value: '其他' },
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
  { prop: 'operator', label: '运营商', width: 100 },
  { prop: 'line_type', label: '线路类型', width: 100 },
  { prop: 'ip_address', label: 'IP', width: 140 },
  { prop: 'mask', label: '掩码', width: 140 },
  { prop: 'gateway', label: '网关', width: 140 },
  { prop: 'dial_account', label: '拨号账号', minWidth: 120 },
  { prop: 'vlan', label: 'VLAN', width: 100 },
  { prop: 'bandwidth', label: '带宽', width: 100 },
  { prop: 'ownership', label: '线路归属', minWidth: 120 },
]

const defaultVisibleColumns = ['id', 'operator', 'line_type', 'ip_address', 'vlan', 'bandwidth', 'ownership']
</script>
