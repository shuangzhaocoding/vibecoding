import request from './request'

export const loginApi = (data) => request.post('/auth/login', data)
export const registerApi = (data) => request.post('/auth/register', data)
export const sendCodeApi = (data) => request.post('/auth/send-code', data)
export const sendResetCodeApi = (data) => request.post('/auth/send-reset-code', data)
export const resetPasswordApi = (data) => request.post('/auth/reset-password', data)
export const logoutApi = () => request.post('/auth/logout')
export const switchRoleApi = (role_id) => request.post('/auth/switch-role', { role_id })
export const meApi = () => request.get('/auth/me')
export const updateProfileApi = (data) => request.patch('/auth/profile', data)
export const changePasswordApi = (data) => request.post('/auth/change-password', data)

export const uploadAvatarApi = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/files/avatar', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
