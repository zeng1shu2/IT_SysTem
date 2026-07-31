/**
 * Port type definitions and port-name generation helpers.
 *
 * Interface types (接口类型):
 *  - 千兆电口  : GigabitEthernet (electrical, 1G)   -> prefix GE   (GE0/0/1)
 *  - 千兆光口  : GigabitEthernet (optical, 1G)      -> prefix GE   (GE0/0/1)
 *  - 万兆光口  : XGigabitEthernet (optical, 10G)    -> prefix XGE  (XGE0/0/1)
 *  - 40G光口   : 40G (optical)                      -> prefix 40XGE(40XGE0/0/1)
 *  - 100G光口  : 100G (optical)                     -> prefix 100XGE(100XGE0/0/1)
 *
 * Port name rule: <prefix><slot>/<subslot>/<index>
 *  - non-stack: slot/subslot = 0/0  -> GE0/0/1
 *  - stack (member m): slot = m     -> GE1/0/1, GE2/0/1 ...
 */

export const PORT_TYPES = [
  { value: 'ge_elec', label: '千兆电口', medium: 'elec', speed: '1g', prefix: 'GE', iface: 'GigabitEthernet' },
  { value: 'ge_opt', label: '千兆光口', medium: 'opt', speed: '1g', prefix: 'GE', iface: 'GigabitEthernet' },
  { value: 'xge_opt', label: '万兆光口', medium: 'opt', speed: '10g', prefix: 'XGE', iface: 'XGigabitEthernet' },
  { value: '40g_opt', label: '40G光口', medium: 'opt', speed: '40g', prefix: '40XGE', iface: '40G' },
  { value: '100g_opt', label: '100G光口', medium: 'opt', speed: '100g', prefix: '100XGE', iface: '100G' },
]

export function getPortType(value) {
  return PORT_TYPES.find((t) => t.value === value) || null
}

/**
 * Expand port groups into a flat list of physical ports.
 * @param {Array} portGroups - [{ type, count }]
 * @param {Object|null} stackConfig - { enabled, count, members }
 * @returns {Array} [{ name, type, typeLabel, medium, speed, prefix, member, index }]
 */
export function generatePorts(portGroups = [], stackConfig = null) {
  const groups = Array.isArray(portGroups) ? portGroups : []
  const stackEnabled = !!(stackConfig && stackConfig.enabled)
  const stackCount = stackEnabled ? Math.max(1, Number(stackConfig.count) || 1) : 0
  const memberLoops = stackEnabled ? stackCount : 1
  const ports = []
  for (let m = 1; m <= memberLoops; m++) {
    const slot = stackEnabled ? m : 0
    groups.forEach((g) => {
      const def = getPortType(g.type)
      if (!def) return
      const count = Number(g.count) || 0
      for (let i = 1; i <= count; i++) {
        ports.push({
          name: `${def.prefix}${slot}/0/${i}`,
          type: def.value,
          typeLabel: def.label,
          medium: def.medium,
          speed: def.speed,
          prefix: def.prefix,
          member: stackEnabled ? m : null,
          index: i,
          net_type: 'access',
          vlan_id: '',
          vlan_range: '',
        })
      }
    })
  }
  return ports
}

/** Total port count from groups (ignores stacking multiplier for the asset summary). */
export function totalPortCount(portGroups = []) {
  if (!Array.isArray(portGroups)) return 0
  return portGroups.reduce((sum, g) => sum + (Number(g.count) || 0), 0)
}

/** Human-readable summary of port groups, e.g. '千兆电口×24，万兆光口×4'. */
export function summarizePortGroups(portGroups = []) {
  if (!Array.isArray(portGroups) || portGroups.length === 0) return '—'
  return portGroups
    .map((g) => {
      const def = getPortType(g.type)
      return `${def ? def.label : g.type}×${Number(g.count) || 0}`
    })
    .join('，')
}

/** Preview range for a single group entry, e.g. 'GE0/0/1 ~ GE0/0/24'. */
export function previewGroupRange(group) {
  const def = getPortType(group?.type)
  const count = Number(group?.count) || 0
  if (!def || count === 0) return '—'
  if (count === 1) return `${def.prefix}0/0/1`
  return `${def.prefix}0/0/1 ~ ${def.prefix}0/0/${count}`
}

/**
 * Build the default ETH interface list for "other / system" device types.
 * Default only one ETH-0 interface (ge_elec). Adding more => ETH-1 ... ETH-N.
 * @param {number} ethCount - number of ETH interfaces (default 1)
 * @returns {Array} [{ name:'ETH-0', type:'eth', typeLabel:'ETH接口', ... }]
 */
export function generateEthPorts(ethCount = 1) {
  const count = Math.max(1, Number(ethCount) || 1)
  const ports = []
  for (let i = 0; i < count; i++) {
    ports.push({
      name: `ETH-${i}`,
      type: 'eth',
      typeLabel: 'ETH接口',
      medium: '',
      speed: '',
      prefix: 'ETH',
      member: null,
      index: i + 1,
      net_type: 'access',
      vlan_id: '',
      vlan_range: '',
    })
  }
  return ports
}

/**
 * Device types that rely on ETH-style interfaces (ETH-0, ETH-1 ...)
 * instead of detailed port groups. Used as a safety net so port-connection
 * can always auto-create at least one ETH port even when eth_count was not
 * persisted (e.g. legacy rows created before the default-value fix).
 * @type {string[]}
 */
const ETH_FAMILY_DEVICE_TYPES = [
  'other', 'hub', 'internet_behavior', 'bastion', 'ips', 'ids',
  'ddos', 'vpn', 'antivirus', 'admission', 'auth', 'nms',
  'database', 'ops_audit', 'api_gateway',
]

/**
 * Resolve physical ports for any device based on its stored config.
 * Priority:
 *  1. typed port_groups (switch/router/firewall with portGroups) -> generatePorts
 *  2. eth_count (other/system/default) -> generateEthPorts (ETH-0 ...)
 *  3. safety net: ETH-family device without any port config -> generateEthPorts(1)
 *  4. legacy fallback: extra_data.port_count -> generic 端口N
 * @returns {Array} flat physical port list
 */
export function resolveAssetPorts(asset) {
  const extra = asset?.extra_data || {}
  if (Array.isArray(extra.port_groups) && extra.port_groups.length > 0) {
    const gen = generatePorts(extra.port_groups, extra.stack_config || null)
    if (gen.length > 0) return gen
  }
  if (extra.eth_count && Number(extra.eth_count) >= 1) {
    return generateEthPorts(extra.eth_count)
  }
  // Safety net: ETH-family devices (e.g. others/security/software systems) that
  // have no explicit port config still auto-create at least ETH-0, mirroring how
  // switches auto-create ports. This guarantees port-connection always has ports
  // to wire, regardless of whether eth_count was persisted.
  const dt = asset?.device_type
  if (dt && ETH_FAMILY_DEVICE_TYPES.includes(dt)) {
    return generateEthPorts(1)
  }
  const fb = Number(extra.port_count) || 0
  if (fb > 0) {
    return Array.from({ length: fb }, (_, i) => ({
      name: `端口${i + 1}`,
      type: '',
      typeLabel: '',
      medium: '',
      speed: '',
      prefix: '',
      member: null,
      index: i + 1,
      net_type: 'access',
      vlan_id: '',
      vlan_range: '',
    }))
  }
  return []
}
