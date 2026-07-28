<template>
  <CrudTablePage
    :api="api"
    form-config-code="ip_plan_form"
    :default-schema="defaultSchema"
    :core-fields="coreFields"
    :columns="columns"
    :default-visible-columns="defaultVisibleColumns"
    title="IP地址规划"
    entity-name="IP规划"
    name-field="ip_range"
    search-placeholder="IP段/部门/小组/VLAN"
    storage-key="ip_plan_columns"
  />
</template>

<script setup>
import CrudTablePage from '@/components/CrudTablePage.vue'
import { getIPPlans, getIPPlan, createIPPlan, updateIPPlan, deleteIPPlan } from '@/api/ip-plan'

const api = { list: getIPPlans, get: getIPPlan, create: createIPPlan, update: updateIPPlan, delete: deleteIPPlan }

const coreFields = ['department', 'group_name', 'ip_range', 'vlan', 'usage_status', 'remark']

const defaultSchema = [
  { type: 'divider', label: '基本信息', span: 24 },
  { type: 'input', label: '部门', prop: 'department', span: 12, placeholder: '如：运维部' },
  { type: 'input', label: '小组', prop: 'group_name', span: 12, placeholder: '如：网络组' },
  { type: 'input', label: 'IP段', prop: 'ip_range', required: true, span: 12, placeholder: '如：192.168.1.0/24' },
  { type: 'input', label: 'VLAN', prop: 'vlan', span: 12, placeholder: '如：VLAN 100' },
  {
    type: 'select', label: '使用状态', prop: 'usage_status', span: 12, defaultValue: 'available',
    options: [
      { label: '可用', value: 'available' },
      { label: '已使用', value: 'used' },
      { label: '已保留', value: 'reserved' },
    ],
  },
  { type: 'textarea', label: '备注', prop: 'remark', span: 24, rows: 2 },
]

const columns = [
  { prop: 'department', label: '部门', minWidth: 120 },
  { prop: 'group_name', label: '小组', minWidth: 120 },
  { prop: 'ip_range', label: 'IP段', minWidth: 150 },
  { prop: 'vlan', label: 'VLAN', width: 100 },
  {
    prop: 'usage_status', label: '使用状态', width: 100, type: 'tag',
    options: [
      { label: '可用', value: 'available' },
      { label: '已使用', value: 'used' },
      { label: '已保留', value: 'reserved' },
    ],
    tagType: (val) => ({ available: 'success', used: 'warning', reserved: 'info' }[val] || ''),
  },
]

const defaultVisibleColumns = ['id', 'department', 'group_name', 'ip_range', 'vlan', 'usage_status']
</script>
