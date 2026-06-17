import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'

const STATION_ORDER = ['NDLS', 'CNB', 'ALD', 'MGS', 'PNBE', 'HWH']

export default function NetworkGraph({ trains, corridor, affectedStations = [] }) {
  const svgRef = useRef(null)
  const containerRef = useRef(null)
  const [tooltip, setTooltip] = useState(null)

  useEffect(() => {
    if (!corridor?.stations || !svgRef.current || !containerRef.current) return

    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight
    const margin = { top: 40, right: 40, bottom: 50, left: 40 }

    const stations = STATION_ORDER.map(id =>
      corridor.stations.find(s => s.id === id)
    ).filter(Boolean)

    const maxKm = stations[stations.length - 1]?.position_km || 1441

    const xScale = d3.scaleLinear()
      .domain([0, maxKm])
      .range([margin.left, width - margin.right])

    const yCenter = height / 2
    const yOffsets = { NDLS: 0, CNB: -15, ALD: 10, MGS: -10, PNBE: 15, HWH: 0 }

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    svg.attr('width', width).attr('height', height)

    const segments = corridor.track_segments || []
    segments.forEach(seg => {
      const from = stations.find(s => s.id === seg.from)
      const to = stations.find(s => s.id === seg.to)
      if (!from || !to) return

      const congested = affectedStations.includes(seg.from) || affectedStations.includes(seg.to)
      svg.append('line')
        .attr('x1', xScale(from.position_km))
        .attr('y1', yCenter + (yOffsets[from.id] || 0))
        .attr('x2', xScale(to.position_km))
        .attr('y2', yCenter + (yOffsets[to.id] || 0))
        .attr('stroke', congested ? '#F59E0B' : '#374151')
        .attr('stroke-width', congested ? 4 : 2)
        .attr('stroke-dasharray', seg.single_track ? '6,4' : null)
    })

    stations.forEach(station => {
      const affected = affectedStations.includes(station.id)
      const hasDelayed = trains.some(t =>
        (t.current_station === station.id || t.next_station === station.id) &&
        t.delay_minutes > 10
      )
      const color = affected || hasDelayed ? '#F59E0B' : '#22C55E'
      const cx = xScale(station.position_km)
      const cy = yCenter + (yOffsets[station.id] || 0)

      const g = svg.append('g').attr('transform', `translate(${cx},${cy})`)

      g.append('circle')
        .attr('r', affected ? 18 : 12)
        .attr('fill', color)
        .attr('opacity', affected ? 0.7 : 1)
        .attr('class', affected ? 'station-alert' : '')

      g.append('text')
        .attr('y', 28)
        .attr('text-anchor', 'middle')
        .attr('fill', '#9CA3AF')
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('font-size', 11)
        .text(station.id)

      g.append('title').text(station.name)
    })

    trains.forEach(train => {
      const fromId = train.current_station
      const toId = train.next_station
      const from = stations.find(s => s.id === fromId)
      const to = stations.find(s => s.id === toId)
      if (!from || !to) return

      const pct = (train.progress_pct || 0) / 100
      const x1 = xScale(from.position_km)
      const y1 = yCenter + (yOffsets[from.id] || 0)
      const x2 = xScale(to.position_km)
      const y2 = yCenter + (yOffsets[to.id] || 0)
      const cx = x1 + (x2 - x1) * pct
      const cy = y1 + (y2 - y1) * pct

      const delayColor = train.delay_minutes > 60 ? '#EF4444'
        : train.delay_minutes > 10 ? '#F59E0B' : (train.color || '#3B82F6')

      const circle = svg.append('circle')
        .attr('cx', cx)
        .attr('cy', cy)
        .attr('r', 8)
        .attr('fill', delayColor)
        .attr('stroke', '#0A0E1A')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')

      if (train.delay_minutes > 10) {
        circle.attr('class', 'thinking-pulse')
      }

      circle
        .on('mouseenter', () => setTooltip({
          x: cx, y: cy - 20,
          name: train.train_name,
          delay: train.delay_minutes,
        }))
        .on('mouseleave', () => setTooltip(null))
    })
  }, [trains, corridor, affectedStations])

  useEffect(() => {
    const handleResize = () => {
      if (corridor?.stations) {
        const event = new Event('resize')
        window.dispatchEvent(event)
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [corridor])

  return (
    <div ref={containerRef} className="relative w-full h-full min-h-[280px] bg-[var(--bg-secondary)] border border-[var(--border)]">
      <div className="absolute top-3 left-4 font-display text-sm text-[var(--text-secondary)]">
        Delhi–Howrah Corridor
      </div>
      <svg ref={svgRef} className="w-full h-full" />
      {tooltip && (
        <div
          className="absolute pointer-events-none bg-[var(--bg-tertiary)] border border-[var(--border)] px-2 py-1 text-xs font-mono rounded z-10"
          style={{ left: tooltip.x, top: tooltip.y, transform: 'translate(-50%, -100%)' }}
        >
          <div className="text-[var(--text-primary)]">{tooltip.name}</div>
          <div className={tooltip.delay > 10 ? 'text-[var(--signal-red)]' : 'text-[var(--signal-green)]'}>
            {tooltip.delay > 10 ? `Delayed +${tooltip.delay} min` : 'On time'}
          </div>
        </div>
      )}
    </div>
  )
}
