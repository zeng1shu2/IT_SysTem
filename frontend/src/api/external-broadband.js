import request from './request'

export function getExternalBroadbands(params) {
  return request.get('/external-broadbands', { params })
}

export function getExternalBroadband(id) {
  return request.get(`/external-broadbands/${id}`)
}

export function createExternalBroadband(data) {
  return request.post('/external-broadbands', data)
}

export function updateExternalBroadband(id, data) {
  return request.put(`/external-broadbands/${id}`, data)
}

export function deleteExternalBroadband(id) {
  return request.delete(`/external-broadbands/${id}`)
}
