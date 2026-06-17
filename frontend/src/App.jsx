import { useCallback, useEffect, useState } from 'react'
import AgentPanel from './components/AgentPanel'
import AuditLog from './components/AuditLog'
import CommunicationDraft from './components/CommunicationDraft'
import ControlBar from './components/ControlBar'
import ImpactDashboard from './components/ImpactDashboard'
import NetworkGraph from './components/NetworkGraph'
import ResponseOptions from './components/ResponseOptions'
import { useWebSocket } from './hooks/useWebSocket'

const INITIAL_AGENTS = {
  monitor: { status: 'idle', output: null },
  cascade: { status: 'idle', output: null },
  impact: { status: 'idle', output: null },
  response: { status: 'idle', output: null },
  comms: { status: 'idle', output: null },
}

const API_BASE = 'http://localhost:8000'

function App() {
  const [trains, setTrains] = useState([])
  const [corridor, setCorridor] = useState(null)
  const [agents, setAgents] = useState(INITIAL_AGENTS)
  const [impact, setImpact] = useState(null)
  const [responses, setResponses] = useState(null)
  const [comms, setComms] = useState(null)
  const [arbitration, setArbitration] = useState(null)
  const [auditLog, setAuditLog] = useState([])
  const [simTime, setSimTime] = useState('--:--')
  const [affectedStations, setAffectedStations] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/api/corridor`)
      .then((r) => r.json())
      .then(setCorridor)
      .catch(console.error)

    const poll = setInterval(() => {
      fetch(`${API_BASE}/api/status`)
        .then((r) => r.json())
        .then((data) => {
          if (data.sim_time) setSimTime(data.sim_time)
        })
        .catch(() => {})
    }, 2000)
    return () => clearInterval(poll)
  }, [])

  const handleWsMessage = useCallback(({ event, payload }) => {
    switch (event) {
      case 'train_update':
        setTrains(payload.trains || [])
        break
      case 'agent_fire':
        setAgents((prev) => ({
          ...prev,
          [payload.agent]: { ...prev[payload.agent], status: 'thinking', output: null },
        }))
        break
      case 'agent_result':
        setAgents((prev) => ({
          ...prev,
          [payload.agent]: { status: payload.status === 'fallback' ? 'fallback' : 'done', output: payload.data },
        }))
        if (payload.agent === 'cascade' && payload.data?.affected_stations) {
          setAffectedStations(payload.data.affected_stations)
        }
        break
      case 'impact_update':
        setImpact(payload)
        break
      case 'response_ready':
        setResponses(payload)
        break
      case 'comms_ready':
        setComms(payload)
        break
      case 'arbitration_done':
        setArbitration(payload)
        break
      case 'audit_entry':
        setAuditLog((prev) => [...prev, payload])
        break
      case 'simulation_reset':
        setTrains([])
        setAgents(INITIAL_AGENTS)
        setImpact(null)
        setResponses(null)
        setComms(null)
        setArbitration(null)
        setAuditLog([])
        setAffectedStations([])
        break
      default:
        break
    }
  }, [])

  const { connected } = useWebSocket(handleWsMessage)

  const handleInject = async (scenarioId) => {
    await fetch(`${API_BASE}/api/inject-delay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: scenarioId }),
    })
  }

  const handleReset = async () => {
    await fetch(`${API_BASE}/api/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
  }

  const handleAccept = (option) => {
    setAuditLog((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        timestamp: new Date().toLocaleTimeString('en-GB'),
        agent: 'operator',
        action: 'Option accepted',
        detail: `Option ${option.id}: ${option.label}`,
        reasoning: `Manual acceptance of recommended response`,
      },
    ])
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] pb-[52px] font-body">
      <header className="h-14 bg-[var(--bg-secondary)] border-b border-[var(--border)] flex items-center justify-between px-4 md:px-6">
        <div>
          <div className="font-display font-bold text-lg text-[var(--signal-amber)] tracking-wide">
            TRACKMIND
          </div>
          <div className="text-xs text-[var(--text-muted)] hidden sm:block">
            Delhi–Howrah Corridor Intelligence System
          </div>
        </div>
        <div className="font-mono text-2xl font-medium text-[var(--text-primary)]">
          {simTime}
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs font-mono text-[var(--signal-green)] live-pulse">
            <span className="w-2 h-2 rounded-full bg-[var(--signal-green)]" />
            LIVE
          </span>
          <span className="text-xs text-[var(--text-muted)] hidden md:inline">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <main className="p-4 max-w-[1600px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">
          <div className="lg:col-span-8 min-h-[300px]">
            <NetworkGraph
              trains={trains}
              corridor={corridor}
              affectedStations={affectedStations}
            />
          </div>
          <div className="lg:col-span-4 min-h-[300px]">
            <AgentPanel agents={agents} arbitration={arbitration} />
          </div>
        </div>

        <div className="mb-4">
          <ImpactDashboard impact={impact} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <ResponseOptions responses={responses} onAccept={handleAccept} />
          <CommunicationDraft comms={comms} />
        </div>

        <AuditLog entries={auditLog} />
      </main>

      <ControlBar
        connected={connected}
        onInject={handleInject}
        onReset={handleReset}
      />
    </div>
  )
}

export default App
