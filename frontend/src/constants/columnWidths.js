/**
 * 字段列宽统一注册表（单一来源 / single source of truth）
 * ------------------------------------------------------------
 * 目的：让"相同字段"在每个列表页都使用同一列宽，避免因各处随手写宽度
 *       导致跨页不一致、不美观。同时统一采用「弹性 min-width」为主，
 *       长文本列会自动撑开显示完整内容（无需手动拉宽），超长时配合
 *       show-overflow-tooltip 悬停查看。
 *
 * 用法：
 *   import { colWidth } from '@/constants/columnWidths'
 *   <el-table-column :min-width="colWidth('device_name')" ... />
 *
 * key 规则：
 *   - 优先使用字段 prop（如 'device_name'、'remark'、'serial_number'）
 *   - 纯展示列（无 prop，如 port-connection 的「设备名称」「VLAN配置」）
 *     使用语义 key（如 'physical_port_overview'、'vlan_config'）
 *
 * 改一处即可全项目同步。新增字段时在此登记即可。
 */

export const FIELD_WIDTHS = {
  // ===== 通用 =====
  id: 70,                 // 已被 IdColumn 固定（保留以便引用一致）
  created_at: 170,
  updated_at: 170,
  operation: 180,         // 操作列统一（原 70~240 不等）
  index: 48,              // # 序号列
  status: 90,
  remark: 160,
  location: 140,
  organization: 120,

  // ===== 资产 / 设备 =====
  device_name: 140,
  device_type: 120,
  brand: 120,
  model: 140,
  serial_number: 150,
  it_asset_code: 140,
  financial_asset_code: 140,
  ip_address: 150,
  mac_address: 160,
  cabinet_u: 120,
  purchase_date: 120,
  warranty_expire: 120,

  // ===== 用户 / 角色 / 权限 =====
  username: 120,
  real_name: 100,
  email: 170,
  phone: 130,
  department: 120,
  is_admin: 80,
  is_active: 90,
  name: 140,              // 角色名称 / 接口名称（语义相近，统一宽度）
  code: 140,              // 角色编码 / 权限编码
  description: 200,
  permissions: 200,

  // ===== 审计 =====
  operator: 120,
  operator_ip: 140,
  last_login_at: 170,
  operation_time: 170,
  operation_type: 100,
  target_type: 100,
  target_id: 80,
  result: 80,
  detail: 260,

  // ===== 权限申请 =====
  applicant: 120,
  permission_code: 140,
  reason: 160,
  auto_rule: 160,
  approved_at: 170,

  // ===== 网络 / IP =====
  ip_range: 160,
  source_device_name: 130,
  source_interface: 140,
  dest_device_name: 130,
  dest_interface: 140,
  connected_device: 140,
  connected_interface: 140,
  network_type: 110,
  local_network_type: 110,
  peer_network_type: 110,
  vlan: 100,
  peer_vlan: 110,
  vlan_id: 100,
  vlan_config: 140,
  ip_mask: 140,
  interface_name: 160,
  member_ports: 240,
  bundle: 110,
  port_count: 110,
  logical_port_count: 110,
  physical_port_overview: 200,
  port_type: 120,

  // ===== 授权管理 =====
  license_key: 160,
  activation_date: 120,
  expiration_date: 120,
  dial_account: 130,
  ownership: 120,
  group_name: 120,
  usage_status: 110,
}

/**
 * 取字段列宽（弹性 min-width）。
 * @param {string} key 字段 key（prop 或语义 key）
 * @param {number} fallback 未登记时的默认最小宽度
 * @returns {number}
 */
export function colWidth(key, fallback = 140) {
  return FIELD_WIDTHS[key] ?? fallback
}
