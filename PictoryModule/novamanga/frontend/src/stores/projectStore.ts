import { create } from 'zustand'
import { projectsAPI } from '../api/client'

interface Project { id: string; name: string; path: string; created_at: number }

interface ProjectStore {
  projects: Project[]
  current: Project | null
  fetchProjects: () => Promise<void>
  fetchProject: (pid: string) => Promise<void>
  createProject: (name: string, path: string) => Promise<Project>
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  current: null,
  fetchProjects: async () => {
    const data = await projectsAPI.list()
    set({ projects: data })
  },
  fetchProject: async (pid) => {
    const data = await projectsAPI.get(pid)
    set({ current: data })
  },
  createProject: async (name, path) => {
    const data = await projectsAPI.create(name, path)
    set(s => ({ projects: [data, ...s.projects] }))
    return data
  },
}))
