import { useEffect, useRef } from 'react'

const AGENT_COLORS = {
  monitor: '#3B82F6',
  cascade: '#8B5CF6',
  impact: '#F59E0B',
  response: '#22C55E',
  comms: '#EC4899',
  arbitrate: '#F97316',
}

export default function AuditLog({ entries }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [entries])

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)]">
      <div className="px-4 py-2 border-b border-[var(--border)]">
        <h2 className="font-display font-semibold text-sm text-[var(--text-secondary)] uppercase tracking-wider">
          Audit Log
        </h2>
      </div>
      <div className="max-h-[200px] overflow-y-auto p-3 font-mono text-xs">
        {entries.length === 0 ? (
          <div className="text-[var(--text-muted)]">No events recorded yet.</div>
        ) : (
          entries.map((entry) => (
            <div key={entry.id} className="py-0.5 leading-5">
              <span className="text-[var(--text-muted)]">[{entry.timestamp}] </span>
              <span
                style={{ color: AGENT_COLORS[entry.agent] || '#9CA3AF' }}
                className="uppercase font-semibold"
              >
                {entry.agent?.padEnd(9)}
              </span>
              <span className="text-[var(--text-primary)]">
                {' '}{entry.action} — {entry.detail}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
