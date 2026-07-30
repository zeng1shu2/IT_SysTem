/**
 * Default asset form schema.
 * Used as fallback when no form config is found in the backend.
 * This schema can be customized via the Form Designer page (code: 'asset_form').
 */
import { DEVICE_CATEGORY_TREE } from '@/constants/vendors'

export const defaultAssetFormSchema = [
  // ===== Basic Info =====
  { type: 'divider', label: '基础信息', span: 24 },
  {
    type: 'input', label: '设备名称', prop: 'device_name', required: true, span: 12,
    placeholder: '如：核心交换机-01',
  },
  {
    // 设备类型：两级联动（大类 → 子类型），避免下拉过长
    type: 'select-cascade', label: '设备类型', prop: 'device_type', required: true, span: 12,
    defaultValue: 'switch',
    cascaderOptions: DEVICE_CATEGORY_TREE,
  },
  // 品牌：与授权管理 license_form.brand 保持一致（select-icon 单选：华为/深信服/绿盟/H3C/信锐）
  {
    type: 'select-icon', label: '品牌', prop: 'brand', span: 12,
    options: [
      { label: '华为', value: '华为', icon: '/brand-icons/huawei.png' },
      { label: '深信服', value: '深信服', icon: '/brand-icons/sangfor.png' },
      { label: '绿盟', value: '绿盟', icon: '/brand-icons/nsfocus.png' },
      { label: 'H3C', value: 'H3C', icon: '/brand-icons/h3c.png' },
      { label: '信锐', value: '信锐', emoji: '📡' },
    ],
  },
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

  // 端口配置（按类型）+ 堆叠 + 管理VLAN：网络设备类（交换机/路由器/集线器/其他设备）与交换机一致
  {
    type: 'portGroups', label: '端口配置（按类型）', prop: 'port_groups', span: 24,
    visibleWhen: { prop: 'device_type', in: ['switch', 'router', 'hub'] },
  },
  {
    type: 'stackConfig', label: '堆叠配置', prop: 'stack_config', span: 24,
    visibleWhen: { prop: 'device_type', in: ['switch', 'router', 'hub'] },
  },
  {
    type: 'input', label: '管理VLAN', prop: 'vlan_range', span: 12,
    placeholder: '如：1-100, 200',
    visibleWhen: { prop: 'device_type', in: ['switch', 'router', 'hub'] },
  },

  // 防火墙：与交换机一致增加端口配置 + 堆叠 + 管理VLAN；安全域改为可多选
  {
    type: 'portGroups', label: '端口配置（按类型）', prop: 'port_groups', span: 24,
    visibleWhen: { prop: 'device_type', equals: 'firewall' },
  },
  {
    type: 'stackConfig', label: '堆叠配置', prop: 'stack_config', span: 24,
    visibleWhen: { prop: 'device_type', equals: 'firewall' },
  },
  {
    type: 'input', label: '管理VLAN', prop: 'vlan_range', span: 12,
    placeholder: '如：1-100, 200',
    visibleWhen: { prop: 'device_type', equals: 'firewall' },
  },

  // 路由器：路由协议改为可多选（其余端口配置已在上方统一块支持）
  {
    type: 'select', label: '路由协议', prop: 'protocol', span: 12,
    defaultValue: [], multiple: true,
    options: [
      { label: 'OSPF', value: 'ospf' },
      { label: 'BGP', value: 'bgp' },
      { label: 'RIP', value: 'rip' },
      { label: '静态路由', value: 'static' },
      { label: 'ISIS', value: 'isis' },
    ],
    visibleWhen: { prop: 'device_type', equals: 'router' },
  },
  {
    type: 'number', label: 'WAN口数', prop: 'wan_count', span: 12,
    min: 0, max: 16,
    visibleWhen: { prop: 'device_type', equals: 'router' },
  },

  // 防火墙：安全域改为可多选（不再只能单选一个域）
  {
    type: 'select', label: '安全域', prop: 'security_zones', span: 12,
    multiple: true,
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

  // 其他设备 / 系统类设备：默认只有一个 ETH-0 接口（ge_elec×1），可新增 ETH-1…
  {
    type: 'input', label: 'ETH接口数', prop: 'eth_count', span: 12,
    defaultValue: 1, min: 1, max: 64,
    placeholder: '默认 1（即 ETH-0），新增则为 ETH-1…',
    visibleWhen: { prop: 'device_type', in: [
      'other', 'hub',
      'internet_behavior', 'bastion', 'ips', 'ids', 'ddos', 'vpn', 'antivirus',
      'admission', 'auth', 'nms', 'database', 'ops_audit', 'api_gateway',
    ] },
  },

  // 安全设备类（非防火墙）子类型 + 防护级别
  {
    type: 'select', label: '安全子类', prop: 'sub_type', span: 12,
    options: [
      { label: 'IDS（入侵检测）', value: 'ids' },
      { label: 'IPS（入侵防御）', value: 'ips' },
      { label: 'WAF（Web应用防火墙）', value: 'waf' },
      { label: '上网行为管理', value: 'behavior' },
    ],
    visibleWhen: { prop: 'device_type', in: ['internet_behavior', 'bastion', 'ips', 'ids', 'ddos', 'vpn', 'antivirus'] },
  },
  {
    type: 'rate', label: '防护级别', prop: 'protection_level', span: 12,
    defaultValue: 3, max: 5,
    visibleWhen: { prop: 'device_type', in: ['internet_behavior', 'bastion', 'ips', 'ids', 'ddos', 'vpn', 'antivirus'] },
  },

  // 其他设备描述
  {
    type: 'textarea', label: '设备描述', prop: 'description', span: 24, rows: 2,
    placeholder: '请描述设备用途...',
    visibleWhen: { prop: 'device_type', in: ['other', 'hub'] },
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
