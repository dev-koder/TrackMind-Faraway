import { useState } from 'react'

export default function ControlBar({ connected, onInject, onReset }) {
  const [showMenu, setShowMenu] = useState(false)
  const [confirmReset, setConfirmReset] = useState(false)

  const handleReset = () => {
    if (!confirmReset) {
      setConfirmReset(true)
      setTimeout(() => setConfirmReset(false), 3000)
      return
    }
    setConfirmReset(false)
    onReset()
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 h-[52px] bg-[var(--bg-secondary)] border-t border-[var(--border)] flex items-center justify-between px-4 z-50">
      <div className="relative">
        <button
          onClick={() => setShowMenu(!showMenu)}
          className="px-4 py-1.5 text-sm bg-[var(--signal-amber)] text-[var(--bg-primary)] font-display font-semibold rounded hover:opacity-90"
        >
          Inject Delay ▼
        </button>
        {showMenu && (
          <div className="absolute bottom-full mb-2 left-0 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded shadow-lg min-w-[240px]">
            <button
              onClick={() => { onInject('scenario_1'); setShowMenu(false) }}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-[var(--bg-highlight)]"
            >
              Scenario 1 — Rajdhani at CNB
            </button>
            <button
              onClick={() => { onInject('scenario_2'); setShowMenu(false) }}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-[var(--bg-highlight)]"
            >
              Scenario 2 — Poorva at ALD
            </button>
          </div>
        )}
      </div>

      <button
        onClick={handleReset}
        className="px-4 py-1.5 text-sm border border-[var(--signal-amber)] text-[var(--signal-amber)] rounded hover:bg-[var(--bg-highlight)] font-display"
      >
        {confirmReset ? 'Confirm Reset?' : 'Reset Simulation'}
      </button>

      <div className="flex items-center gap-4 text-xs font-mono text-[var(--text-secondary)]">
        <span>60× speed</span>
        <div className="flex items-center gap-1.5">
          <span>WS</span>
          <div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: connected ? 'var(--signal-green)' : 'var(--signal-red)' }}
          />
        </div>
      </div>
    </div>
  )
}
