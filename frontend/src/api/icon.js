/**
 * 图标库 (Icon) API。
 *
 * - 上传通过 multipart/form-data，文件字段名为 file。
 * - 后端路径：/api/v1/icons（router 已注册在 icons.py）。
 */
import request from '@/api/request'

// 列出图标（可按 category / keyword 过滤）
export async function listIcons(params = {}) {
  const res = await request.get('/icons', { params })
  return res || { total: 0, items: [] }
}

// 上传图标（multipart）
// payload: { file: File, name: string, category?: string }
export async function uploadIcon(payload) {
  const fd = new FormData()
  fd.append('file', payload.file)
  fd.append('name', payload.name || payload.file.name)
  if (payload.category) fd.append('category', payload.category)
  const res = await request.post('/icons/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res
}

// 软删除（仅管理员，禁用）
export async function deleteIcon(id) {
  return request.delete(`/icons/${id}`)
}

// 物理删除（仅管理员，删库 + 删磁盘文件，不可逆）
export async function permanentDeleteIcon(id) {
  return request.delete(`/icons/${id}/permanent`)
}

// 常用分类常量（与后端约定保持一致）
export const ICON_CATEGORIES = [
  { value: 'device', label: '设备类型' },
  { value: 'brand', label: '品牌' },
  { value: 'operator', label: '运营商' },
  { value: 'other', label: '其他' },
]