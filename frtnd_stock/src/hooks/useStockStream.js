import { useEffect, useState } from 'react'

export function useStockStream() {
  const [prices, setPrices] = useState({})
  const [alerts, setAlerts] = useState([])
  const [news, setNews] = useState([])
  const [connected, setConnected] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    const es = new EventSource('/api/stream')

    es.addEventListener('prices', (e) => {
      setPrices(JSON.parse(e.data))
      setLastUpdated(new Date())
    })

    es.addEventListener('alert', (e) => {
      const alert = JSON.parse(e.data)
      setAlerts((prev) => [alert, ...prev].slice(0, 30))
    })

    // initial dump of existing alerts on connect
    es.addEventListener('alerts', (e) => {
      setAlerts(JSON.parse(e.data))
    })

    es.addEventListener('news', (e) => {
      setNews(JSON.parse(e.data))
    })

    es.onopen = () => setConnected(true)
    es.onerror = () => setConnected(false)

    return () => es.close()
  }, [])

  return { prices, alerts, news, connected, lastUpdated }
}
