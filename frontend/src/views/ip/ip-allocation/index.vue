<template>
  <CrudTablePage
    :api="api"
    form-config-code="ip_allocation_form"
    :default-schema="defaultSchema"
    :core-fields="coreFields"
    :columns="columns"
    :default-visible-columns="defaultVisibleColumns"
    title="IP地址分配表"
    entity-name="IP分配"
    name-field="ip_address"
    search-placeholder="部门/使用人/IP地址/登记人"
    storage-key="ip_allocation_columns"
  />
</template>

<script setup>
import CrudTablePage from '@/components/CrudTablePage.vue'
import {
  getIPAllocations, getIPAllocation,
  createIPAllocation, updateIPAllocation, deleteIPAllocation,
} from '@/api/ip-allocation'

const api = {
  list: getIPAllocations, get: getIPAllocation,
  create: createIPAllocation, update: updateIPAllocation, delete: deleteIPAllocation,
}

// 全部为主表字段（core），便于按部门/使用人等查询
const coreFields = ['department', 'user_name', 'ip_address', 'apply_date', 'recycle_date', 'remark', 'registrar']

const defaultSchema = [
  { type: 'divider', label: '基本信息', span: 24 },
  { type: 'input', label: '部门', prop: 'department', span: 12, placeholder: '如：运维部' },
  { type: 'input', label: '使用人', prop: 'user_name', span: 12, placeholder: '如：张三' },
  { type: 'input', label: 'IP地址/掩码', prop: 'ip_address', required: true, span: 12, placeholder: '如：192.168.1.10/24' },
  { type: 'input', label: '登记人', prop: 'registrar', span: 12, placeholder: '如：李四' },
  { type: 'date', label: '申请日期', prop: 'apply_date', span: 12 },
  { type: 'date', label: '回收日期', prop: 'recycle_date', span: 12 },
  { type: 'textarea', label: '备注', prop: 'remark', span: 24, rows: 2 },
]

const columns = [
  { prop: 'department', label: '部门', width: 120 },
  { prop: 'user_name', label: '使用人', width: 120 },
  { prop: 'ip_address', label: 'IP地址/掩码', minWidth: 160 },
  { prop: 'apply_date', label: '申请日期', width: 120, type: 'date' },
  { prop: 'recycle_date', label: '回收日期', width: 120, type: 'date' },
  { prop: 'registrar', label: '登记人', width: 100 },
]

const defaultVisibleColumns = ['id', 'department', 'user_name', 'ip_address', 'apply_date', 'recycle_date', 'registrar']
</script>
