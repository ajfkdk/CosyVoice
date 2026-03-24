import { useEffect } from 'react'
import { useTaskStore } from '../stores/taskStore'

export function useSSE(refIds: string[]) {
  const addEvent = useTaskStore(s => s.addEvent)

  useEffect(() => {
    if (!refIds.length) return
    const ids = refIds.join(',')
    const es = new EventSource(`/api/sse/tasks?ref_ids=${encodeURIComponent(ids)}`)
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type !== 'heartbeat' && data.task_id) {
          const refId = refIds.find(id => data.task_id) || refIds[0]
          addEvent(refId, data)
        }
      } catch {}
    }
    return () => es.close()
  }, [refIds.join(',')])
}
