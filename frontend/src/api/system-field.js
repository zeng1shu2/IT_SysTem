/**
 * 字段管理 (SystemField) API + schema 选项注入 helper。
 *
 * 设计目标（需求 #3）：表单里凡标记 source==='system_field' 的字段，
 * 其下拉选项不再写死在前端/后端种子里，而是运行时从 /system-fields/options/{code}
 * 拉取。这样后续要在字段管理页新增一个类型/选项，无需改任何代码即可在所有表单生效。
 */
import request from '@/api/request'

// 获取某个受管字段的动态选项
// - 扁平字段: [{label, value, icon?, emoji?, sort}]
// - device_type: 两级树 [{label, options:[{label, value, icon?, emoji?}]}]
export async function getFieldOptions(code) {
  try {
    const res = await request.get(`/system-fields/options/${code}`)
    return res || []
  } catch {
    return []
  }
}

// 列出某字段的所有选项行（含停用），用于字段管理页
export async function listSystemFields(field_code) {
  const res = await request.get('/system-fields', { params: { field_code } })
  return res || { total: 0, items: [] }
}

export async function createSystemField(payload) {
  return request.post('/system-fields', payload)
}

export async function updateSystemField(id, payload) {
  return request.put(`/system-fields/${id}`, payload)
}

export async function deleteSystemField(id) {
  return request.delete(`/system-fields/${id}`)
}

/**
 * 把 schema 中 source==='system_field' 的字段选项动态注入。
 * 返回新的 schema 数组（不修改原数组，便于 Vue 响应式更新）。
 * 若拉取到的选项为空，则保留字段原有的 options（fallback），避免下拉变空。
 */
export async function resolveSystemFieldOptions(fields) {
  if (!Array.isArray(fields)) return fields
  const codes = new Set()
  fields.forEach((f) => {
    if (f && f.source === 'system_field' && f.sourceCode) codes.add(f.sourceCode)
  })
  if (codes.size === 0) return fields
  const map = {}
  await Promise.all(
    [...codes].map(async (code) => {
      map[code] = await getFieldOptions(code)
    })
  )
  return fields.map((f) => {
    if (f && f.source === 'system_field' && f.sourceCode && map[f.sourceCode] && map[f.sourceCode].length) {
      const opts = map[f.sourceCode]
      if (f.type === 'select-cascade') {
        return { ...f, cascaderOptions: opts }
      }
      return { ...f, options: opts }
    }
    return f
  })
}

// 由 device_type 树构建 value→label 映射（用于表格显示动态类型名）
export function buildDeviceTypeLabelMap(tree) {
  const map = {}
  ;(tree || []).forEach((cat) => {
    ;(cat.options || []).forEach((sub) => {
      map[sub.value] = sub.label
    })
  })
  return map
}

// 7 个受管字段的元数据（字段管理页左侧分组用）
export const FIELD_GROUPS = [
  { code: 'organization', name: '组织', type: 'flat' },
  { code: 'location', name: '位置', type: 'flat' },
  { code: 'brand', name: '品牌', type: 'flat' },
  { code: 'device_type', name: '设备类型', type: 'tree' },
  { code: 'security_zones', name: '安全域', type: 'flat' },
  { code: 'protocol', name: '路由协议', type: 'flat' },
  { code: 'operator', name: '运营商', type: 'flat' },
]
