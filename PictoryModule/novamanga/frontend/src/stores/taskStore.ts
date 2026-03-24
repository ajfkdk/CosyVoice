import { create } from 'zustand'

interface TaskEvent {
  task_id: string
  type: string
  status: string
  result?: unknown
  error?: string
}

interface TaskStore {
  events: Record<string, TaskEvent[]>
  addEvent: (refId: string, event: TaskEvent) => void
  getLatest: (refId: string) => TaskEvent | null
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  events: {},
  addEvent: (refId, event) => {
    set(s => ({
      events: {
        ...s.events,
        [refId]: [...(s.events[refId] || []), event],
      }
    }))
  },
  getLatest: (refId) => {
    const evs = get().events[refId]
    return evs && evs.length > 0 ? evs[evs.length - 1] : null
  },
}))
