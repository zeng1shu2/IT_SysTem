import request from './request'

export function getIPPlans(params) {
  return request.get('/ip-plans', { params })
}

export function getIPPlan(id) {
  return request.get(`/ip-plans/${id}`)
}

export function createIPPlan(data) {
  return request.post('/ip-plans', data)
}

export function updateIPPlan(id, data) {
  return request.put(`/ip-plans/${id}`, data)
}

export function deleteIPPlan(id) {
  return request.delete(`/ip-plans/${id}`)
}
