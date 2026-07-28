import request from './request'

export function getPermissionCatalog() {
  return request.get('/permissions/catalog')
}

export function getPermissionRequests(params) {
  return request.get('/permissions', { params })
}

export function applyPermission(data) {
  return request.post('/permissions/apply', data)
}
