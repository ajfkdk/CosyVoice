import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useProjectStore } from '../stores/projectStore'
import { chaptersAPI } from '../api/client'

interface Chapter { id: string; title: string; parse_status: string; order_index: number }

export default function ProjectDashboard() {
  const { pid } = useParams<{ pid: string }>()
  const nav = useNavigate()
  const { current, fetchProject } = useProjectStore()
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [newTitle, setNewTitle] = useState('')

  useEffect(() => {
    if (pid) {
      fetchProject(pid)
      chaptersAPI.list(pid).then(setChapters)
    }
  }, [pid])

  const addChapter = async () => {
    if (!newTitle.trim() || !pid) return
    const ch = await chaptersAPI.create(pid, newTitle, chapters.length)
    setChapters(prev => [...prev, ch])
    setNewTitle('')
  }

  const statusColor = (s: string) => ({
    idle: 'text-gray-500', processing: 'text-yellow-400', completed: 'text-green-400', failed: 'text-red-400'
  }[s] || 'text-gray-500')

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <button onClick={() => nav('/projects')} className="text-gray-500 hover:text-white">← 返回</button>
          <h1 className="text-2xl font-bold text-white">{current?.name || '...'}</h1>
        </div>

        <div className="flex gap-4 mb-8">
          <button onClick={() => nav(`/projects/${pid}/characters`)} className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg">角色管理</button>
          <button onClick={() => nav(`/projects/${pid}/timeline`)} className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg">时间轴预览</button>
        </div>

        <div className="space-y-3">
          {chapters.map(ch => (
            <div
              key={ch.id}
              onClick={() => nav(`/projects/${pid}/chapters/${ch.id}`)}
              className="bg-gray-900 border border-gray-800 hover:border-indigo-500 rounded-xl p-5 cursor-pointer flex justify-between items-center transition"
            >
              <span className="text-white font-medium">{ch.title}</span>
              <span className={`text-sm ${statusColor(ch.parse_status)}`}>{ch.parse_status}</span>
            </div>
          ))}
        </div>

        <div className="flex gap-3 mt-6">
          <input
            className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            placeholder="章节标题，如：第一章 我们离婚吧"
            onKeyDown={e => e.key === 'Enter' && addChapter()}
          />
          <button onClick={addChapter} className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg">添加</button>
        </div>
      </div>
    </div>
  )
}
