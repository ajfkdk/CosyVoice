import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { zonesAPI } from '../api/client'
import { useProjectStore } from '../stores/projectStore'

interface Zone {
  id: string; text_content: string; emotion_primary: string; emotion_intensity: number
  prompt_positive: string; prompt_negative: string; image_asset_id: string | null
}

export default function ZoneEditor() {
  const { pid, cid, zid } = useParams<{ pid: string; cid: string; zid: string }>()
  const nav = useNavigate()
  const { current, fetchProject } = useProjectStore()
  const [zone, setZone] = useState<Zone | null>(null)
  const [promptPos, setPromptPos] = useState('')
  const [promptNeg, setPromptNeg] = useState('')
  const [genPromptLoading, setGenPromptLoading] = useState(false)
  const [genImgLoading, setGenImgLoading] = useState(false)
  const [imgPath, setImgPath] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState('')

  useEffect(() => {
    if (pid) fetchProject(pid)
  }, [pid])

  useEffect(() => {
    if (!zid || !current) return
    zonesAPI.get(zid, current.path).then((z: Zone) => {
      setZone(z)
      setPromptPos(z.prompt_positive || '')
      setPromptNeg(z.prompt_negative || '')
      if (z.image_asset_id) {
        setImgPath(`/api/zones/${zid}/image?project_path=${encodeURIComponent(current.path)}`)
      }
    })
  }, [zid, current])

  const generatePrompt = async () => {
    if (!current || !zid) return
    setGenPromptLoading(true)
    setTaskStatus('正在生成 Prompt...')
    await zonesAPI.generatePrompt(zid, current.path)
    const poll = setInterval(async () => {
      const z = await zonesAPI.get(zid, current.path)
      if (z.prompt_positive) {
        setPromptPos(z.prompt_positive)
        setPromptNeg(z.prompt_negative || '')
        setZone(z)
        setGenPromptLoading(false)
        setTaskStatus('Prompt 生成完成')
        clearInterval(poll)
      }
    }, 2000)
    setTimeout(() => { clearInterval(poll); setGenPromptLoading(false) }, 30000)
  }

  const generateImage = async () => {
    if (!current || !zid) return
    setGenImgLoading(true)
    setTaskStatus('正在生成图片...')
    await zonesAPI.generateImage(zid, current.path, { prompt_positive: promptPos, prompt_negative: promptNeg })
    const poll = setInterval(async () => {
      const z = await zonesAPI.get(zid, current.path)
      if (z.image_asset_id) {
        setZone(z)
        setImgPath(`/api/zones/${zid}/image?project_path=${encodeURIComponent(current.path)}&t=${Date.now()}`)
        setGenImgLoading(false)
        setTaskStatus('图片生成完成')
        clearInterval(poll)
      }
    }, 3000)
    setTimeout(() => { clearInterval(poll); setGenImgLoading(false) }, 120000)
  }

  const savePrompt = async () => {
    if (!current || !zid) return
    await zonesAPI.update(zid, current.path, { prompt_positive: promptPos, prompt_negative: promptNeg })
    setTaskStatus('Prompt 已保存')
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => nav(`/projects/${pid}/chapters/${cid}`)} className="text-gray-500 hover:text-white">← 返回</button>
          <h1 className="text-xl font-bold text-white">句区编辑器</h1>
          {taskStatus && <span className="text-sm text-indigo-400 ml-auto">{taskStatus}</span>}
        </div>

        {zone && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                <div className="text-xs text-gray-500 mb-2">句区文本</div>
                <p className="text-gray-200 leading-relaxed">{zone.text_content}</p>
              </div>
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                <div className="text-xs text-gray-500 mb-2">情绪</div>
                <p className="text-white">{zone.emotion_primary} <span className="text-gray-400">强度 {Math.round(zone.emotion_intensity * 100)}%</span></p>
              </div>
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-xs text-gray-500">Prompt (Positive)</div>
                  <button onClick={generatePrompt} disabled={genPromptLoading} className="text-xs bg-indigo-700 hover:bg-indigo-600 text-white px-3 py-1 rounded">
                    {genPromptLoading ? '生成中...' : 'AI 生成'}
                  </button>
                </div>
                <textarea
                  className="w-full bg-gray-800 text-gray-200 text-xs rounded p-2 outline-none resize-none h-24"
                  value={promptPos}
                  onChange={e => setPromptPos(e.target.value)}
                />
                <div className="text-xs text-gray-500 mt-2 mb-1">Prompt (Negative)</div>
                <textarea
                  className="w-full bg-gray-800 text-gray-200 text-xs rounded p-2 outline-none resize-none h-16"
                  value={promptNeg}
                  onChange={e => setPromptNeg(e.target.value)}
                />
                <div className="flex gap-2 mt-2">
                  <button onClick={savePrompt} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-xs py-1.5 rounded">保存 Prompt</button>
                  <button onClick={generateImage} disabled={genImgLoading || !promptPos} className="flex-1 bg-purple-700 hover:bg-purple-600 text-white text-xs py-1.5 rounded disabled:opacity-50">
                    {genImgLoading ? '生成中...' : '生成图片'}
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-800 flex items-center justify-center min-h-64">
              {imgPath ? (
                <img src={imgPath} alt="生成图片" className="w-full h-full object-contain rounded-xl" />
              ) : (
                <div className="text-center text-gray-600">
                  <div className="text-4xl mb-2">🖼</div>
                  <div className="text-sm">{genImgLoading ? '图片生成中...' : '暂无图片'}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
