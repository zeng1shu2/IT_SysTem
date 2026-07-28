import request from './request'

/** 获取表单配置列表 */
export function getFormConfigs(params) {
  return request.get('/form-configs', { params })
}

/** 按 ID 获取表单配置 */
export function getFormConfig(id) {
  return request.get(`/form-configs/${id}`)
}

/** 按编码获取表单配置 */
export function getFormConfigByCode(code) {
  return request.get(`/form-configs/code/${code}`, { skipErrorHandler: true })
}

/** 创建表单配置 */
export function createFormConfig(data) {
  return request.post('/form-configs', data)
}

/** 更新表单配置 */
export function updateFormConfig(id, data) {
  return request.put(`/form-configs/${id}`, data)
}

/** 删除表单配置 */
export function deleteFormConfig(id) {
  return request.delete(`/form-configs/${id}`)
}
