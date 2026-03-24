import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ProjectList from './pages/ProjectList'
import ProjectDashboard from './pages/ProjectDashboard'
import ChapterEditor from './pages/ChapterEditor'
import ZoneEditor from './pages/ZoneEditor'
import CharacterAssets from './pages/CharacterAssets'
import Timeline from './pages/Timeline'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectList />} />
        <Route path="/projects/:pid" element={<ProjectDashboard />} />
        <Route path="/projects/:pid/chapters/:cid" element={<ChapterEditor />} />
        <Route path="/projects/:pid/chapters/:cid/zones/:zid" element={<ZoneEditor />} />
        <Route path="/projects/:pid/characters" element={<CharacterAssets />} />
        <Route path="/projects/:pid/timeline" element={<Timeline />} />
      </Routes>
    </BrowserRouter>
  )
}
