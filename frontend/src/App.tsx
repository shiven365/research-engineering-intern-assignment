import { Route, Routes } from 'react-router-dom'
import Overview from './pages/Overview'
import Timeline from './pages/Timeline'
import NetworkPage from './pages/Network'
import ClustersPage from './pages/Clusters'
import ChatPage from './pages/Chat'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Overview />} />
      <Route path="/timeline" element={<Timeline />} />
      <Route path="/network" element={<NetworkPage />} />
      <Route path="/clusters" element={<ClustersPage />} />
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  )
}
