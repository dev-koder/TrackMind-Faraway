import { useEffect, useState } from 'react'

const TABS = ['English', 'Hindi', 'SMS', 'Ops Log']

function TypewriterText({ text, speed = 15 }) {
  const [displayed, setDisplayed] = useState('')

  useEffect(() => {
    setDisplayed('')
    if (!text) return
    let i = 0
    const timer = setInterval(() => {
      i++
      setDisplayed(text.slice(0, i))
      if (i >= text.length) clearInterval(timer)
    }, speed)
    return () => clearInterval(timer)
  }, [text, speed])

  return <span>{displayed}</span>
}

export default function CommunicationDraft({ comms }) {
  const [activeTab, setActiveTab] = useState('English')

  if (!comms) return null

  const copyText = () => {
    let text = ''
    if (activeTab === 'English') text = comms.station_announcement?.english || ''
    else if (activeTab === 'Hindi') text = comms.station_announcement?.hindi || ''
    else if (activeTab === 'SMS') text = comms.sms_draft || ''
    else text = comms.operations_log || ''
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] p-4 slide-up">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display font-semibold text-sm text-[var(--text-secondary)] uppercase tracking-wider">
          Communication Draft
        </h2>
        <button
          onClick={copyText}
          className="text-xs px-2 py-1 border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] rounded"
        >
          Copy
        </button>
      </div>

      <div className="flex gap-1 mb-4 border-b border-[var(--border)]">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1.5 text-xs font-mono transition-colors ${
              activeTab === tab
                ? 'text-[var(--signal-amber)] border-b-2 border-[var(--signal-amber)]'
                : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="min-h-[100px] text-sm leading-relaxed">
        {activeTab === 'English' && (
          <TypewriterText text={comms.station_announcement?.english} />
        )}
        {activeTab === 'Hindi' && (
          <div className="text-base">
            <TypewriterText text={comms.station_announcement?.hindi} />
          </div>
        )}
        {activeTab === 'SMS' && (
          <div>
            <div className="inline-block bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-2xl px-4 py-3 max-w-xs">
              <TypewriterText text={comms.sms_draft} />
            </div>
            <div className="text-xs text-[var(--text-muted)] mt-2 font-mono">
              {(comms.sms_draft || '').length} / 160 characters
            </div>
          </div>
        )}
        {activeTab === 'Ops Log' && (
          <pre className="font-mono text-xs text-[var(--text-secondary)] whitespace-pre-wrap">
            <TypewriterText text={comms.operations_log} speed={8} />
          </pre>
        )}
      </div>
    </div>
  )
}
