// 厂商/品牌共享选项 — 资产.品牌 与 授权.品牌 共用同一份选项列表。
// 修改此处即同步更新两处下拉。
export const VENDOR_OPTIONS = [
  { label: '华为', value: '华为' },
  { label: '深信服', value: '深信服' },
  { label: '绿盟', value: '绿盟' },
  { label: 'H3C', value: 'H3C' },
  { label: '信锐', value: '信锐' },
]

// 厂商 → Logo key 映射（用于品牌图标渲染）
export const VENDOR_LOGO_KEYS = {
  huawei:  ['华为', 'huawei'],
  sangfor: ['深信服', 'sangfor'],
  nsfocus: ['绿盟', 'nsfocus'],
  h3c:     ['H3C', 'h3c', '华三', '新华三'],
  xinrui:  ['信锐', 'xinrui'],
}

// 大类 → 设备类型 树（资产.设备类型 两级下拉使用）
// 与后端 main.py seed / assetFormSchema 保持一致
export const DEVICE_CATEGORY_TREE = [
  {
    label: '网络设备类',
    options: [
      { label: '交换机', value: 'switch' },
      { label: '路由器', value: 'router' },
      { label: '集线器', value: 'hub' },
      { label: '其他设备', value: 'other' },
    ],
  },
  {
    label: '安全设备类',
    options: [
      { label: '防火墙', value: 'firewall' },
      { label: '上网行为管理', value: 'internet_behavior' },
      { label: '堡垒机', value: 'bastion' },
      { label: 'IPS', value: 'ips' },
      { label: 'IDS', value: 'ids' },
      { label: 'DDoS', value: 'ddos' },
      { label: 'VPN', value: 'vpn' },
      { label: '杀毒软件', value: 'antivirus' },
    ],
  },
  {
    label: '其他软件类',
    options: [
      { label: '准入系统', value: 'admission' },
      { label: '认证系统', value: 'auth' },
      { label: '网管系统', value: 'nms' },
      { label: '数据库系统', value: 'database' },
      { label: '运维审计系统', value: 'ops_audit' },
      { label: 'API网关系统', value: 'api_gateway' },
    ],
  },
]

// value → 中文标签 快速查找
export const DEVICE_TYPE_LABEL_MAP = DEVICE_CATEGORY_TREE.reduce((acc, cat) => {
  cat.options.forEach((o) => { acc[o.value] = o.label })
  return acc
}, {})

export function deviceTypeLabel(val) {
  if (!val) return '未分类'
  return DEVICE_TYPE_LABEL_MAP[val] || val
}

/**
 * 设备类型 → 图标（emoji 优先；如有 PNG 则写 icon 路径）。
 * 后续临时新增类型若图标不准确，用户可在此补充 PNG / emoji 后优化。
 * 约定占位 emoji：
 *   网络设备类 → 🌐 / 具体设备有专属 emoji
 *   安全设备类 → 🛡
 *   其他软件类 → 🧩
 */
export const DEVICE_TYPE_ICON = {
  // 网络设备类
  switch: { emoji: '🔀' },
  router: { emoji: '📡' },
  hub: { emoji: '🔌' },
  other: { emoji: '📦' },
  // 安全设备类
  firewall: { emoji: '🛡' },
  internet_behavior: { emoji: '🚦' },
  bastion: { emoji: '🔐' },
  ips: { emoji: '🛡' },
  ids: { emoji: '🔍' },
  ddos: { emoji: '🌊' },
  vpn: { emoji: '🔗' },
  antivirus: { emoji: '🦠' },
  // 其他软件类
  admission: { emoji: '🧩' },
  auth: { emoji: '🔑' },
  nms: { emoji: '🛰' },
  database: { emoji: '🗄' },
  ops_audit: { emoji: '📋' },
  api_gateway: { emoji: '🔁' },
  // 临时 / 未知类型的占位（用户后续可补充具体图标）
  custom: { emoji: '❔' },
}

export function getDeviceTypeIcon(val) {
  if (!val) return { emoji: '❔' }
  return DEVICE_TYPE_ICON[val] || { emoji: '❔' }
}

/**
 * 扁平化设备类型列表（用于单级下拉 / 搜索过滤 / select-grouped 的 option 构建）。
 * 每项: { label, value, category }
 */
export const FLAT_DEVICE_TYPES = DEVICE_CATEGORY_TREE.reduce((acc, cat) => {
  cat.options.forEach((o) => {
    acc.push({ label: o.label, value: o.value, category: cat.label })
  })
  return acc
}, [])

/**
 * 哪些设备类型需要「端口配置 + 堆叠 + VLAN」动态特性（与交换机一致）。
 *  - 网络设备类全部：switch / router / hub / other
 *  - 安全设备（非纯软件）：firewall（堡垒机/IP/IDS 等纯逻辑设备可不配物理口，但为统一仍给予）
 *  - 其他软件类为纯逻辑系统，默认只有一个 ETH-0 接口（也可新增 ETH-1…），故也纳入。
 */
export const PORT_CAPABLE_DEVICE_TYPES = [
  'switch', 'router', 'hub', 'other',
  'firewall', 'internet_behavior', 'bastion', 'ips', 'ids', 'ddos', 'vpn', 'antivirus',
  'admission', 'auth', 'nms', 'database', 'ops_audit', 'api_gateway',
]

/** 默认仅一个 ETH-0 接口的设备类型集合（无 typed 端口时按 ETH-0 兜底）。 */
export const DEFAULT_ETH_ONLY_TYPES = [
  'hub', 'other',
  'firewall', 'internet_behavior', 'bastion', 'ips', 'ids', 'ddos', 'vpn', 'antivirus',
  'admission', 'auth', 'nms', 'database', 'ops_audit', 'api_gateway',
]
