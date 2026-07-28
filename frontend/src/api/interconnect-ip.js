import request from './request'

export function getInterconnectIPs(params) {
  return request.get('/interconnect-ips', { params })
}

export function getInterconnectIP(id) {
  return request.get(`/interconnect-ips/${id}`)
}

export function createInterconnectIP(data) {
  return request.post('/interconnect-ips', data)
}

export function updateInterconnectIP(id, data) {
  return request.put(`/interconnect-ips/${id}`, data)
}

export function deleteInterconnectIP(id) {
  return request.delete(`/interconnect-ips/${id}`)
}
