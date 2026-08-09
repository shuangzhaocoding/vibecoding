import request from './request'

export const fetchAuthor = (userId, params) =>
  request.get(`/authors/${userId}`, { params })

export const fetchNotifications = (params) =>
  request.get('/notifications', { params })

export const fetchUnreadCount = () =>
  request.get('/notifications/unread-count')

export const markAllNotificationsRead = () =>
  request.post('/notifications/read-all')

export const markNotificationRead = (id) =>
  request.post(`/notifications/${id}/read`)
