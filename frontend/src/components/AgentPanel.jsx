import { Eye, GitBranch, Users, Zap, Radio } from 'lucide-react'

const AGENT_CONFIG = [
  { key: 'monitor', name: 'Monitor', icon: Eye, idleText: 'Monitoring corridor...' },
  { key: 'cascade', name: 'Cascade', icon: GitBranch, idleText: 'Awaiting delay signal...' },
  { key: 'impact', name: 'Impact', icon: Users, idleText: 'Standing by...' },
  { key: 'response', name: 'Response', icon: Zap, idleText: 'Standing by...' },
  { key: 'comms', name: 'Comms', icon: Radio, idleText: 'Standing by...' },
]

const STATUS_COLORS = {
  idle: 'var(--agent-idle)',
  thinking: 'var(--agent-thinking)',
  done: 'var(--agent-done)',
  fallback: 'var(--agent-fallback)',
  error: 'var(--agent-error)',
}

function getStatusText(agent) {
  if (!agent || agent.status === 'idle') return null
  if (agent.status === 'thinking') return 'Analysing...'
  if (agent.output?.message) return agent.output.message
  if (agent.output?.without_intervention) return agent.output.without_intervention
  if (agent.output?.narrative) return agent.output.narrative.split('.')[0]
  if (agent.output?.recommendation) return `Option ${agent.output.recommendation} recommended`
  if (agent.output?.operations_log) return 'Announcements drafted'
  return 'Complete'
}

export default function AgentPanel({ agents, arbitration }) {
  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] p-4 h-full flex flex-col">
      <h2 className="font-display font-semibold text-sm text-[var(--text-secondary)] mb-4 uppercase tracking-wider">
        Agent Activity
      </h2>

      <div className="flex-1 space-y-3">
        {AGENT_CONFIG.map(({ key, name, icon: Icon, idleText }) => {
          const agent = agents[key] || { status: 'idle', output: null }
          const statusText = getStatusText(agent) || idleText
          const dotColor = STATUS_COLORS[agent.status] || STATUS_COLORS.idle

          return (
            <div
              key={key}
              className="flex items-center gap-3 p-2 rounded bg-[var(--bg-tertiary)]"
            >
              <Icon size={18} className="text-[var(--text-muted)] shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-display font-semibold text-sm">{name}</div>
                <div className="text-xs text-[var(--text-secondary)] truncate">{statusText}</div>
              </div>
              <div
                className={`w-3 h-3 rounded-full shrink-0 ${agent.status === 'thinking' ? 'thinking-pulse' : ''}`}
                style={{ backgroundColor: dotColor }}
              />
            </div>
          )
        })}
      </div>

      {arbitration && (
        <div className="mt-4 p-3 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded slide-up">
          <div className="font-display font-semibold text-sm text-[var(--signal-amber)] mb-2">
            Arbitration
          </div>
          <div className="text-sm font-mono mb-2">
            Option {arbitration.recommendation} — {(arbitration.confidence * 100).toFixed(0)}% confidence
          </div>
          {arbitration.vote_breakdown && (
            <div className="space-y-1">
              {Object.entries(arbitration.vote_breakdown).map(([agent, vote]) => (
                <div key={agent} className="flex items-center gap-2 text-xs">
                  <span className="text-[var(--text-muted)] w-16 capitalize">{agent}</span>
                  <div className="flex-1 h-2 bg-[var(--bg-primary)] rounded overflow-hidden">
                    <div
                      className="h-full bg-[var(--signal-green)]"
                      style={{ width: `${(vote.weight / 3) * 100}%` }}
                    />
                  </div>
                  <span className="font-mono text-[var(--text-secondary)]">
                    {vote.vote} (w:{vote.weight})
                  </span>
                </div>
              ))}
            </div>
          )}
          {arbitration.human_review_needed && (
            <div className="mt-2 text-xs text-[var(--signal-amber)]">Human review recommended</div>
          )}
        </div>
      )}
    </div>
  )
}
