import CountUp from 'react-countup'

function getColor(value, type) {
  if (!value || value === 0) return 'var(--text-muted)'
  if (type === 'passengers') {
    if (value >= 2000) return 'var(--signal-red)'
    if (value >= 500) return 'var(--signal-amber)'
    return 'var(--signal-green)'
  }
  if (type === 'connections') {
    if (value >= 100) return 'var(--signal-red)'
    if (value >= 50) return 'var(--signal-amber)'
    return 'var(--signal-green)'
  }
  if (value >= 3) return 'var(--signal-red)'
  if (value >= 1) return 'var(--signal-amber)'
  return 'var(--signal-green)'
}

export default function ImpactDashboard({ impact }) {
  const passengers = impact?.total_passengers_affected || 0
  const connections = impact?.missed_connections || 0
  const trains = impact?.trains_impacted || 0
  const score = impact?.impact_score || 0
  const hasData = passengers > 0

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] p-4">
      {!hasData && (
        <div className="text-sm text-[var(--text-muted)] mb-2">Monitoring corridor...</div>
      )}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div
            className="font-display font-bold text-4xl md:text-5xl"
            style={{ color: getColor(passengers, 'passengers') }}
          >
            {hasData ? <CountUp end={passengers} duration={1.5} separator="," /> : '0'}
          </div>
          <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider mt-1">
            Passengers Affected
          </div>
        </div>
        <div>
          <div
            className="font-display font-bold text-4xl md:text-5xl"
            style={{ color: getColor(connections, 'connections') }}
          >
            {hasData ? <CountUp end={connections} duration={1.5} /> : '0'}
          </div>
          <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider mt-1">
            Missed Connections
          </div>
        </div>
        <div>
          <div
            className="font-display font-bold text-4xl md:text-5xl"
            style={{ color: getColor(trains, 'trains') }}
          >
            {hasData ? <CountUp end={trains} duration={1.5} /> : '0'}
          </div>
          <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider mt-1">
            Trains Impacted
          </div>
        </div>
      </div>
      {score > 0 && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-[var(--text-secondary)] mb-1">
            <span>Impact Score</span>
            <span>{score.toFixed(1)} / 10</span>
          </div>
          <div className="h-1.5 bg-[var(--bg-primary)] rounded overflow-hidden">
            <div
              className="h-full rounded transition-all duration-1000"
              style={{
                width: `${(score / 10) * 100}%`,
                background: `linear-gradient(90deg, var(--signal-amber), var(--signal-red))`,
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
