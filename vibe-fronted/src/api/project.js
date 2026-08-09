import request from './request'

export const fetchProjects = (params) => request.get('/projects', { params })
export const fetchProjectTags = (params) => request.get('/projects/tags', { params })
export const fetchRanking = (params) => request.get('/projects/ranking', { params })
export const fetchCreatorDashboard = (params) => request.get('/projects/dashboard', { params })
export const fetchProject = (id) => request.get(`/projects/${id}`)
export const createProject = (data) => request.post('/projects', data)
export const updateProject = (id, data) => request.patch(`/projects/${id}`, data)
export const deleteProject = (id) => request.delete(`/projects/${id}`)
export const likeProject = (id) => request.post(`/projects/${id}/like`)
export const unlikeProject = (id) => request.delete(`/projects/${id}/like`)
export const favoriteProject = (id) => request.post(`/projects/${id}/favorite`)
export const unfavoriteProject = (id) => request.delete(`/projects/${id}/favorite`)
export const fetchComments = (id, params) => request.get(`/projects/${id}/comments`, { params })
export const createComment = (id, data) => request.post(`/projects/${id}/comments`, data)
export const deleteComment = (projectId, commentId) =>
  request.delete(`/projects/${projectId}/comments/${commentId}`)
export const reportProject = (id, data) => request.post(`/projects/${id}/report`, data)
export const fetchReports = (params) => request.get('/projects/reports', { params })
export const resolveReport = (id, data) => request.post(`/projects/reports/${id}/resolve`, data)

export const uploadFile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/files/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
