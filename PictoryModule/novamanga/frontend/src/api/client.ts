import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const projectsAPI = {
  list: () => api.get('/projects').then(r => r.data),
  create: (name: string, path: string) => api.post('/projects', { name, path }).then(r => r.data),
  get: (pid: string) => api.get(`/projects/${pid}`).then(r => r.data),
}

export const chaptersAPI = {
  list: (pid: string) => api.get(`/projects/${pid}/chapters`).then(r => r.data),
  create: (pid: string, title: string, order_index = 0) =>
    api.post(`/projects/${pid}/chapters`, { title, order_index }).then(r => r.data),
  update: (cid: string, projectPath: string, data: Record<string, unknown>) =>
    api.put(`/chapters/${cid}`, data, { params: { project_path: projectPath } }).then(r => r.data),
  parse: (cid: string, projectPath: string) =>
    api.post(`/chapters/${cid}/parse`, null, { params: { project_path: projectPath } }).then(r => r.data),
}

export const zonesAPI = {
  list: (cid: string, projectPath: string) =>
    api.get(`/chapters/${cid}/zones`, { params: { project_path: projectPath } }).then(r => r.data),
  get: (zid: string, projectPath: string) =>
    api.get(`/zones/${zid}`, { params: { project_path: projectPath } }).then(r => r.data),
  update: (zid: string, projectPath: string, data: Record<string, unknown>) =>
    api.put(`/zones/${zid}`, data, { params: { project_path: projectPath } }).then(r => r.data),
  generatePrompt: (zid: string, projectPath: string) =>
    api.post(`/zones/${zid}/prompt/generate`, null, { params: { project_path: projectPath } }).then(r => r.data),
  generateImage: (zid: string, projectPath: string, body: Record<string, unknown> = {}) =>
    api.post(`/zones/${zid}/image/generate`, body, { params: { project_path: projectPath } }).then(r => r.data),
}

export const charactersAPI = {
  list: (pid: string, projectPath: string) =>
    api.get(`/projects/${pid}/characters`, { params: { project_path: projectPath } }).then(r => r.data),
  create: (pid: string, projectPath: string, name: string, raw_description: string) =>
    api.post(`/projects/${pid}/characters`, { name, raw_description }, { params: { project_path: projectPath } }).then(r => r.data),
  variants: (charId: string, projectPath: string) =>
    api.get(`/characters/${charId}/variants`, { params: { project_path: projectPath } }).then(r => r.data),
}
