import request from './request'

export function getPortConnections(params) {
  return request.get('/port-connections', { params })
}

export function getPortConnection(id) {
  return request.get(`/port-connections/${id}`)
}

export function getPortConnectionByAssetId(assetId) {
  return request.get(`/port-connections/by-asset/${assetId}`, { skipErrorHandler: true })
}

export function getReverseLinks(deviceId, portNames) {
  return request.get('/port-connections/reverse-links', {
    params: { device_id: deviceId, port_names: (portNames || []).join(',') },
  })
}

export function createPortConnection(data) {
  return request.post('/port-connections', data)
}

export function updatePortConnection(id, data) {
  return request.put(`/port-connections/${id}`, data)
}

export function deletePortConnection(id) {
  return request.delete(`/port-connections/${id}`)
}
