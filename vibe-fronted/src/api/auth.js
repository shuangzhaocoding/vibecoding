import request from './request'

export const loginApi = (data) => request.post('/auth/login', data)
export const registerApi = (data) => request.post('/auth/register', data)
export const sendCodeApi = (data) => request.post('/auth/send-code', data)
export const logoutApi = () => request.post('/auth/logout')
export const switchRoleApi = (role_id) => request.post('/auth/switch-role', { role_id })
export const meApi = () => request.get('/auth/me')
