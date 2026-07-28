import request from './request'

export function getLicenses(params) {
  return request.get('/licenses', { params })
}

export function getLicense(id) {
  return request.get(`/licenses/${id}`)
}

export function createLicense(data) {
  return request.post('/licenses', data)
}

export function updateLicense(id, data) {
  return request.put(`/licenses/${id}`, data)
}

export function deleteLicense(id) {
  return request.delete(`/licenses/${id}`)
}
