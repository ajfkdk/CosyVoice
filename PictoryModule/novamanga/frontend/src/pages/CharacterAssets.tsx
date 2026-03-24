import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { charactersAPI } from '../api/client'
import { useProjectStore } from '../stores/projectStore'

interface Character { id: string; name: string; raw_description: string; personality_tags: string; color_tendency: string }

export default function CharacterAssets() {
  const { pid } = useParams<{ pid: string }>()
  const nav = useNavigate()
  const { current, fetchProject } = useProjectStore()
  const [chars, setChars] = useState<Character[]>([])
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')

  useEffect(() => {
    if (pid) fetchProject(pid)
  }, [pid])

  useEffect(() => {
    if (!current || !pid) return
    charactersAPI.list(pid, current.path).then(setChars)
  }, [current, pid])

  const addChar = async () => {
    if (!name.trim() || !current || !pid) return
    const c = await charactersAPI.create(pid, current.path, name, desc)
    setChars(prev => [...prev, c])
    setShowModal(false)
    setName(''); setDesc('')
  }

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <button onClick={() => nav(`/projects/${pid}`)} className="text-gray-500 hover:text-white">← 返回</button>
          <h1 className="text-2xl font-bold text-white">角色资产</h1>
          <button onClick={() => setShowModal(true)} className="ml-auto bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg">+ 添加角色</button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {chars.map(c => {
            let tags: string[] = []
            try { tags = JSON.parse(c.personality_tags) } catch {}
            return (
              <div key={c.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white">{c.name}</h2>
                {c.color_tendency && <p className="text-xs text-indigo-400 mt-1">{c.color_tendency}</p>}
                <p className="text-gray-400 text-sm mt-2 line-clamp-2">{c.raw_description}</p>
                {tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {tags.map((t, i) => <span key={i} className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded">{t}</span>)}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {chars.length === 0 && (
          <div className="text-center text-gray-600 py-20">暂无角色，点击右上角添加</div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-2xl p-8 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-6">添加角色</h2>
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm">角色名</label>
                <input className="w-full mt-1 bg-gray-800 text-white rounded-lg px-4 py-2 outline-none" value={name} onChange={e => setName(e.target.value)} placeholder="如：林知命" />
              </div>
              <div>
                <label className="text-gray-400 text-sm">外貌描述（用于 AI 提取）</label>
                <textarea className="w-full mt-1 bg-gray-800 text-white rounded-lg px-4 py-2 outline-none resize-none h-24" value={desc} onChange={e => setDesc(e.target.value)} placeholder="从小说中复制角色相关描述..." />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="flex-1 bg-gray-700 text-white py-2 rounded-lg">取消</button>
              <button onClick={addChar} className="flex-1 bg-indigo-600 text-white py-2 rounded-lg">创建</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
