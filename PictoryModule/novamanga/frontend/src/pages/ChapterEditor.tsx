import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { chaptersAPI, zonesAPI } from '../api/client'
import { useProjectStore } from '../stores/projectStore'

interface Zone { id: string; order_index: number; text_content: string; emotion_primary: string; emotion_intensity: number; image_asset_id: string | null; prompt_positive: string }

export default function ChapterEditor() {
  const { pid, cid } = useParams<{ pid: string; cid: string }>()
  const nav = useNavigate()
  const { current, fetchProject } = useProjectStore()
  const [chapter, setChapter] = useState<{ title: string; raw_text: string; parse_status: string } | null>(null)
  const [zones, setZones] = useState<Zone[]>([])
  const [rawText, setRawText] = useState('')
  const [saving, setSaving] = useState(false)
  const [parsing, setParsing] = useState(false)

  useEffect(() => {
    if (pid) fetchProject(pid)
  }, [pid])

  useEffect(() => {
    if (!cid || !current) return
    chaptersAPI.list(pid!).then((chs: { id: string; title: string; raw_text: string; parse_status: string }[]) => {
      const ch = chs.find(c => c.id === cid)
      if (ch) { setChapter(ch); setRawText(ch.raw_text) }
    })
    zonesAPI.list(cid, current.path).then(setZones)
  }, [cid, current])

  const save = async () => {
    if (!current) return
    setSaving(true)
    await chaptersAPI.update(cid!, current.path, { raw_text: rawText })
    setSaving(false)
  }

  const parse = async () => {
    if (!current) return
    setParsing(true)
    await chaptersAPI.update(cid!, current.path, { raw_text: rawText })
    await chaptersAPI.parse(cid!, current.path)
    const poll = setInterval(async () => {
      const zs = await zonesAPI.list(cid!, current.path)
      if (zs.length > 0) {
        setZones(zs)
        setParsing(false)
        clearInterval(poll)
      }
    }, 2000)
    setTimeout(() => { clearInterval(poll); setParsing(false) }, 60000)
  }

  const emotionColor = (e: string) => ({
    恐惧: 'bg-purple-900/60 border-purple-600',
    紧张: 'bg-yellow-900/60 border-yellow-600',
    悲痛: 'bg-blue-900/60 border-blue-600',
    愤怒: 'bg-red-900/60 border-red-600',
    震撼: 'bg-orange-900/60 border-orange-600',
    平静: 'bg-gray-800/60 border-gray-600',
    欢快: 'bg-green-900/60 border-green-600',
    温柔: 'bg-pink-900/60 border-pink-600',
  }[e] || 'bg-gray-800/60 border-gray-600')

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <div className="flex items-center gap-4 p-4 border-b border-gray-800">
        <button onClick={() => nav(`/projects/${pid}`)} className="text-gray-500 hover:text-white">← 返回</button>
        <h1 className="text-lg font-bold text-white flex-1">{chapter?.title || '...'}</h1>
        <span className="text-sm text-gray-500">{chapter?.parse_status}</span>
        <button onClick={save} disabled={saving} className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-1.5 rounded-lg text-sm">
          {saving ? '保存中...' : '保存'}
        </button>
        <button onClick={parse} disabled={parsing} className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg text-sm">
          {parsing ? '解析中...' : '解析分镜'}
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/2 flex flex-col border-r border-gray-800">
          <div className="p-3 text-xs text-gray-500 border-b border-gray-800">原文编辑</div>
          <textarea
            className="flex-1 bg-transparent text-gray-200 p-4 resize-none outline-none text-sm leading-relaxed"
            value={rawText}
            onChange={e => setRawText(e.target.value)}
            placeholder="在此粘贴章节原文..."
          />
        </div>

        <div className="w-1/2 overflow-y-auto">
          <div className="p-3 text-xs text-gray-500 border-b border-gray-800">分镜句区（{zones.length}个）</div>
          {parsing && (
            <div className="p-4 text-center text-yellow-400 text-sm animate-pulse">AI 正在分析分镜...</div>
          )}
          <div className="p-3 space-y-2">
            {zones.map(z => (
              <div
                key={z.id}
                onClick={() => nav(`/projects/${pid}/chapters/${cid}/zones/${z.id}`)}
                className={`border rounded-lg p-3 cursor-pointer hover:opacity-80 transition ${emotionColor(z.emotion_primary)}`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-gray-300">{z.emotion_primary} {Math.round(z.emotion_intensity * 100)}%</span>
                  {z.image_asset_id && <span className="text-xs text-green-400">有图</span>}
                  {z.prompt_positive && !z.image_asset_id && <span className="text-xs text-blue-400">有Prompt</span>}
                </div>
                <p className="text-sm text-gray-200 line-clamp-2">{z.text_content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
