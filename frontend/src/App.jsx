import { Route, Routes } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import PumpDetail from './pages/PumpDetail'
import PumpList from './pages/PumpList'
import AIInsights from './pages/AIInsights'
import AlertManagement from './pages/AlertManagement'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden text-industrial-text">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/pumps" element={<PumpList />} />
          <Route path="/pumps/:id" element={<PumpDetail />} />
          <Route path="/insights" element={<AIInsights />} />
          <Route path="/alerts" element={<AlertManagement />} />
        </Routes>
      </main>
    </div>
  )
}
