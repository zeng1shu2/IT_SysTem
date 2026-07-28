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
    search-placeholder="厂商/设备名称/设备类型"
    storage-key="license_columns"
  />
</template>

<script setup>
import CrudTablePage from '@/components/CrudTablePage.vue'
import {
  getLicenses, getLicense,
  createLicense, updateLicense, deleteLicense,
} from '@/api/license'

const api = {
  list: getLicenses, get: getLicense,
  create: createLicense, update: updateLicense, delete: deleteLicense,
}

const coreFields = [
  'vendor', 'device_type', 'asset_id', 'device_name',
  'license_key', 'activation_date', 'expiration_date', 'remark',
]

const defaultSchema = [
  { type: 'divider', label: '授权信息', span: 24 },
  { type: 'input', label: '厂商', prop: 'vendor', span: 12, placeholder: '如：华为' },
  { type: 'input', label: '设备类型', prop: 'device_type', span: 12, placeholder: '如：防火墙' },
  { type: 'input', label: '设备名称', prop: 'device_name', span: 12, placeholder: '关联资产统计中的设备' },
  { type: 'input', label: '授权码', prop: 'license_key', span: 12, placeholder: '授权码/序列号' },
  { type: 'date', label: '激活日期', prop: 'activation_date', span: 12 },
  { type: 'date', label: '到期日期', prop: 'expiration_date', span: 12 },
  { type: 'textarea', label: '备注', prop: 'remark', span: 24, rows: 2 },
]

const columns = [
  { prop: 'vendor', label: '厂商', width: 120 },
  { prop: 'device_type', label: '设备类型', width: 120 },
  { prop: 'device_name', label: '设备名称', minWidth: 120 },
  { prop: 'license_key', label: '授权码', minWidth: 150 },
  { prop: 'activation_date', label: '激活日期', width: 120, type: 'date' },
  { prop: 'expiration_date', label: '到期日期', width: 120, type: 'date' },
]

const defaultVisibleColumns = ['id', 'vendor', 'device_type', 'device_name', 'activation_date', 'expiration_date']
</script>
