export function formatNumber(n) {
  if (n == null) return '0'
  return n.toLocaleString('en-IN')
}

export function formatTime(timeStr) {
  return timeStr || '--:--'
}

export function formatDelay(minutes) {
  if (!minutes || minutes <= 0) return 'On time'
  return `+${minutes} min`
}
