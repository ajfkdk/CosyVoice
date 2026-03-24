import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjectStore } from '../stores/projectStore'

export default function ProjectList() {
  const { projects, fetchProjects, createProject } = useProjectStore()
  const nav = useNavigate()
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [path, setPath] = useState('C:\\temp\\novamanga_')

  useEffect(() => { fetchProjects() }, [])

  const handleCreate = async () => {
    if (!name.trim()) return
    const p = await createProject(name, path + name)
    setShowModal(false)
    setName('')
    nav(`/projects/${p.id}`)
  }

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">NovaManga</h1>
          <button
            onClick={() => setShowModal(true)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg"
          >
            + 新建项目
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="text-center text-gray-500 py-20">暂无项目，点击右上角新建</div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {projects.map(p => (
              <div
                key={p.id}
                onClick={() => nav(`/projects/${p.id}`)}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6 cursor-pointer hover:border-indigo-500 transition"
              >
                <h2 className="text-xl font-semibold text-white">{p.name}</h2>
                <p className="text-gray-500 text-sm mt-1">{p.path}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-2xl p-8 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-6">新建项目</h2>
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm">项目名称</label>
                <input
                  className="w-full mt-1 bg-gray-800 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="如：我们离婚吧"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm">存储路径</label>
                <input
                  className="w-full mt-1 bg-gray-800 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                  value={path + name}
                  onChange={e => setPath(e.target.value)}
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg">取消</button>
              <button onClick={handleCreate} className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg">创建</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
