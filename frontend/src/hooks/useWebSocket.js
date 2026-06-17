import { useCallback, useEffect, useRef, useState } from 'react'

const WS_URL = 'ws://localhost:8000/ws'

export function useWebSocket(onMessage) {
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)
  const onMessageRef = useRef(onMessage)

  onMessageRef.current = onMessage

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessageRef.current?.(data)
      } catch (err) {
        console.error('WebSocket parse error:', err)
      }
    }

    ws.onclose = () => {
      setConnected(false)
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { connected }
}
