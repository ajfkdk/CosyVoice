import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { chaptersAPI, zonesAPI } from '../api/client'
import { useProjectStore } from '../stores/projectStore'

interface Zone { id: string; text_content: string; emotion_primary: string; emotion_intensity: number; image_asset_id: string | null; duration_ms: number | null }

export default function Timeline() {
  const { pid } = useParams<{ pid: string }>()
  const nav = useNavigate()
  const { current, fetchProject } = useProjectStore()
  const [allZones, setAllZones] = useState<Zone[]>([])
  const [activeIdx, setActiveIdx] = useState(0)
  const [playing, setPlaying] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (pid) fetchProject(pid)
  }, [pid])

  useEffect(() => {
    if (!current || !pid) return
    chaptersAPI.list(pid).then(async (chs: { id: string }[]) => {
      const zoneGroups = await Promise.all(chs.map(ch => zonesAPI.list(ch.id, current.path)))
      setAllZones(zoneGroups.flat())
    })
  }, [current, pid])

  useEffect(() => {
    if (!playing || allZones.length === 0) return
    const dur = (allZones[activeIdx]?.duration_ms || 3000)
    timerRef.current = setTimeout(() => {
      if (activeIdx < allZones.length - 1) setActiveIdx(i => i + 1)
      else setPlaying(false)
    }, dur)
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [playing, activeIdx, allZones])

  const emotionBg = (e: string) => ({
    恐惧: '#3b0764', 紧张: '#713f12', 悲痛: '#1e3a5f', 愤怒: '#7f1d1d',
    震撼: '#7c2d12', 平静: '#1f2937', 欢快: '#14532d', 温柔: '#500724',
  }[e] || '#1f2937')

  const active = allZones[activeIdx]

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <div className="flex items-center gap-4 p-4 border-b border-gray-800">
        <button onClick={() => nav(`/projects/${pid}`)} className="text-gray-500 hover:text-white">← 返回</button>
        <h1 className="text-lg font-bold text-white">时间轴预览</h1>
        <span className="text-gray-500 text-sm">{allZones.length} 个句区</span>
      </div>

      {active && (
        <div className="flex-1 flex items-center justify-center p-8 transition-all duration-500"
          style={{ background: `radial-gradient(ellipse at center, ${emotionBg(active.emotion_primary)} 0%, #030712 70%)` }}>
          <div className="max-w-2xl text-center">
            <div className="text-xs text-gray-500 mb-4">{active.emotion_primary} · {Math.round(active.emotion_intensity * 100)}%</div>
            <p className="text-2xl text-white leading-relaxed font-light">{active.text_content}</p>
          </div>
        </div>
      )}

      <div className="border-t border-gray-800 p-4">
        <div className="flex items-center gap-4 mb-3">
          <button onClick={() => setActiveIdx(i => Math.max(0, i - 1))} className="text-gray-400 hover:text-white px-3 py-1">◀</button>
          <button onClick={() => setPlaying(p => !p)} className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg">
            {playing ? '⏸ 暂停' : '▶ 播放'}
          </button>
          <button onClick={() => setActiveIdx(i => Math.min(allZones.length - 1, i + 1))} className="text-gray-400 hover:text-white px-3 py-1">▶</button>
          <span className="text-gray-500 text-sm">{activeIdx + 1} / {allZones.length}</span>
        </div>

        <div className="flex gap-1 overflow-x-auto pb-2">
          {allZones.map((z, i) => (
            <div
              key={z.id}
              onClick={() => { setActiveIdx(i); setPlaying(false) }}
              className={`flex-shrink-0 w-16 h-10 rounded cursor-pointer border transition ${i === activeIdx ? 'border-indigo-500' : 'border-gray-800'}`}
              style={{ background: emotionBg(z.emotion_primary) }}
              title={z.text_content.slice(0, 30)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
