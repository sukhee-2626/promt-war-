import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import Landing      from './pages/Landing'
import Onboarding   from './pages/Onboarding'
import Dashboard    from './pages/Dashboard'
import CareerMatch  from './pages/CareerMatch'
import Roadmap      from './pages/Roadmap'
import Assess       from './pages/Assess'
import Progress     from './pages/Progress'
import AgentActivity from './pages/AgentActivity'
import Pivot        from './pages/Pivot'
import Resources    from './pages/Resources'
import Resume       from './pages/Resume'
import Outreach     from './pages/Outreach'
import Practice     from './pages/Practice'
import Interview    from './pages/Interview'
import NotFound     from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route element={<Layout />}>
          <Route path="/dashboard/:userId"             element={<Dashboard />} />
          <Route path="/match/:userId"                 element={<CareerMatch />} />
          <Route path="/roadmap/:userId"               element={<Roadmap />} />
          <Route path="/assess/:userId/:skillId"       element={<Assess />} />
          <Route path="/progress/:userId"              element={<Progress />} />
          <Route path="/agent-activity/:userId/:roadmapId" element={<AgentActivity />} />
          <Route path="/pivot/:userId"                 element={<Pivot />} />
          <Route path="/resume/:userId"                element={<Resume />} />
          <Route path="/outreach/:userId"              element={<Outreach />} />
          <Route path="/outreach"                      element={<Outreach />} />
          <Route path="/resources/:skillId"            element={<Resources />} />
          <Route path="/practice/:userId"              element={<Practice />} />
          <Route path="/interview/:userId"             element={<Interview />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
