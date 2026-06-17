export default function ResponseOptions({ responses, onAccept }) {
  if (!responses?.options?.length) return null

  const { options, recommendation } = responses

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] p-4 slide-up">
      <h2 className="font-display font-semibold text-sm text-[var(--text-secondary)] mb-4 uppercase tracking-wider">
        Response Options
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {options.map((option) => {
          const isRecommended = option.id === recommendation
          return (
            <div
              key={option.id}
              className="relative p-4 bg-[var(--bg-tertiary)] rounded"
              style={{
                borderLeft: `3px solid ${isRecommended ? 'var(--signal-green)' : 'var(--border)'}`,
              }}
            >
              {isRecommended && (
                <span className="absolute top-2 right-2 text-xs font-mono text-[var(--signal-green)] bg-[var(--bg-primary)] px-2 py-0.5 rounded">
                  RECOMMENDED
                </span>
              )}
              <div className="font-mono text-xs text-[var(--text-muted)] mb-1">
                OPTION {option.id}
              </div>
              <div className="font-display font-semibold text-lg mb-3">{option.label}</div>
              <div className="space-y-2 text-sm">
                <Row label="Action" value={option.action} />
                <Row label="Delay Cost" value={`+${option.delay_cost_minutes} minutes`} />
                <Row label="Passengers Saved" value={option.passengers_saved} />
                <Row label="Risk" value={option.risk} />
                <Row
                  label="Optimises For"
                  value={option.optimizes_for === 'passenger_service' ? 'Passenger Service' : 'Efficiency'}
                />
              </div>
              <button
                onClick={() => onAccept(option)}
                className="mt-4 w-full py-2 text-sm border border-[var(--border-active)] text-[var(--signal-amber)] hover:bg-[var(--bg-highlight)] transition-colors rounded"
              >
                Accept
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div>
      <span className="text-[var(--text-muted)]">{label}: </span>
      <span className="text-[var(--text-primary)]">{value}</span>
    </div>
  )
}
