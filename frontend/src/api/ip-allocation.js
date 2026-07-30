import request from './request'

export function getIPAllocations(params) {
  return request.get('/ip-allocations', { params })
}

export function getIPAllocation(id) {
  return request.get(`/ip-allocations/${id}`)
}

export function createIPAllocation(data) {
  return request.post('/ip-allocations', data)
}

export function updateIPAllocation(id, data) {
  return request.put(`/ip-allocations/${id}`, data)
}

export function deleteIPAllocation(id) {
  return request.delete(`/ip-allocations/${id}`)
}
