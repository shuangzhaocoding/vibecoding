import request from './request'

export const fetchUsers = (params) => request.get('/users', { params })
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.patch(`/users/${id}`, data)
export const assignUserPermissions = (id, permission_ids) =>
  request.put(`/users/${id}/permissions`, { permission_ids })

export const fetchRoles = () => request.get('/roles')
export const createRole = (data) => request.post('/roles', data)
export const updateRole = (id, data) => request.patch(`/roles/${id}`, data)
export const deleteRole = (id) => request.delete(`/roles/${id}`)
export const assignRolePermissions = (id, permission_ids) =>
  request.put(`/roles/${id}/permissions`, { permission_ids })

export const fetchPermissions = () => request.get('/permissions')
export const createPermission = (data) => request.post('/permissions', data)
export const updatePermission = (id, data) => request.patch(`/permissions/${id}`, data)
export const deletePermission = (id) => request.delete(`/permissions/${id}`)
