/**
 * Default asset form schema.
 * Used as fallback when no form config is found in the backend.
 * This schema can be customized via the Form Designer page (code: 'asset_form').
 */
export const defaultAssetFormSchema = [
  // ===== Basic Info =====
  { type: 'divider', label: '基础信息', span: 24 },
  {
    type: 'input', label: '设备名称', prop: 'device_name', required: true, span: 12,
    placeholder: '如：核心交换机-01',
  },
  {
    type: 'select', label: '设备类型', prop: 'device_type', required: true, span: 12,
    defaultValue: 'switch',
    options: [
      { label: '交换机', value: 'switch' },
      { label: '路由器', value: 'router' },
      { label: '防火墙', value: 'firewall' },
      { label: '安全设备', value: 'security' },
      { label: '其他设备', value: 'other' },
    ],
  },
  { type: 'input', label: '品牌', prop: 'brand', span: 12, placeholder: '如：华为' },
  { type: 'input', label: '型号', prop: 'model', span: 12, placeholder: '如：S5700-28C-HI' },

  // ===== Network Info =====
  { type: 'divider', label: '网络信息', span: 24 },
  {
    type: 'input', label: '管理IP', prop: 'ip_address', span: 12,
    placeholder: '如：192.168.1.1',
  },
  {
    type: 'input', label: 'MAC地址', prop: 'mac_address', span: 12,
    placeholder: '如：00:1A:2B:3C:4D:5E',
  },

  // ===== Dynamic Fields (conditional on device_type) =====
  { type: 'divider', label: '设备特性（动态）', span: 24 },

  // Switch: typed port groups + stacking + VLAN range
  {
    type: 'portGroups', label: '端口配置（按类型）', prop: 'port_groups', span: 24,
    visibleWhen: { prop: 'device_type', equals: 'switch' },
  },
  {
    type: 'stackConfig', label: '堆叠配置', prop: 'stack_config', span: 24,
    visibleWhen: { prop: 'device_type', equals: 'switch' },
  },
  {
    type: 'input', label: '管理VLAN', prop: 'vlan_range', span: 12,
    placeholder: '如：1-100, 200',
    visibleWhen: { prop: 'device_type', equals: 'switch' },
  },

  // Router: protocol + WAN count
  {
    type: 'select', label: '路由协议', prop: 'protocol', span: 12,
    defaultValue: [],
    options: [
      { label: 'OSPF', value: 'ospf' },
      { label: 'BGP', value: 'bgp' },
      { label: 'RIP', value: 'rip' },
      { label: '静态路由', value: 'static' },
    ],
    visibleWhen: { prop: 'device_type', equals: 'router' },
  },
  {
    type: 'number', label: 'WAN口数', prop: 'wan_count', span: 12,
    min: 0, max: 16,
    visibleWhen: { prop: 'device_type', equals: 'router' },
  },

  // Firewall: security zone + policy count
  {
    type: 'select', label: '安全域', prop: 'security_zone', span: 12,
    options: [
      { label: 'Trust（信任）', value: 'trust' },
      { label: 'Untrust（不信任）', value: 'untrust' },
      { label: 'DMZ（隔离区）', value: 'dmz' },
      { label: '自定义', value: 'custom' },
    ],
    visibleWhen: { prop: 'device_type', equals: 'firewall' },
  },
  {
    type: 'number', label: '策略数', prop: 'policy_count', span: 12,
    defaultValue: 0, min: 0, max: 9999,
    visibleWhen: { prop: 'device_type', equals: 'firewall' },
  },

  // Security: sub type + protection level
  {
    type: 'select', label: '安全子类', prop: 'sub_type', span: 12,
    options: [
      { label: 'IDS（入侵检测）', value: 'ids' },
      { label: 'IPS（入侵防御）', value: 'ips' },
      { label: 'WAF（Web应用防火墙）', value: 'waf' },
      { label: '上网行为管理', value: 'behavior' },
    ],
    visibleWhen: { prop: 'device_type', equals: 'security' },
  },
  {
    type: 'rate', label: '防护级别', prop: 'protection_level', span: 12,
    defaultValue: 3, max: 5,
    visibleWhen: { prop: 'device_type', equals: 'security' },
  },

  // Other: description
  {
    type: 'textarea', label: '设备描述', prop: 'description', span: 24, rows: 2,
    placeholder: '请描述设备用途...',
    visibleWhen: { prop: 'device_type', equals: 'other' },
  },

  // ===== Location & Status =====
  { type: 'divider', label: '资产编码', span: 24 },
  { type: 'input', label: 'IT资产编码', prop: 'it_asset_code', span: 12, placeholder: '如：IT-2024-0001' },
  { type: 'input', label: '财务资产编码', prop: 'financial_asset_code', span: 12, placeholder: '如：FA-2024-0001' },
  { type: 'divider', label: '位置与状态', span: 24 },
  { type: 'input', label: '序列号', prop: 'serial_number', span: 12, placeholder: '设备序列号' },
  {
    type: 'select', label: '状态', prop: 'status', required: true, span: 12,
    defaultValue: 'in_use',
    options: [
      { label: '使用中', value: 'in_use' },
      { label: '空闲', value: 'idle' },
      { label: '故障', value: 'fault' },
      { label: '维护中', value: 'maintenance' },
      { label: '已报废', value: 'scrap' },
    ],
  },
  { type: 'input', label: '存放位置', prop: 'location', span: 24, placeholder: '如：机房A-机柜03-U12' },
  { type: 'date', label: '采购日期', prop: 'purchase_date', span: 12 },
  { type: 'date', label: '保修到期', prop: 'warranty_expire', span: 12 },
  { type: 'textarea', label: '备注', prop: 'remark', span: 24, rows: 2 },
]

/**
 * Core fields that map to backend Asset model columns.
 * Extra fields from the designer schema that don't exist in the backend model
 * will be stored in the `extra_data` JSON column (if available) or ignored.
 */
export const coreAssetFields = [
  'device_name', 'device_type', 'brand', 'model',
  'serial_number', 'it_asset_code', 'financial_asset_code',
  'ip_address', 'mac_address', 'location',
  'status', 'purchase_date', 'warranty_expire', 'remark',
]
