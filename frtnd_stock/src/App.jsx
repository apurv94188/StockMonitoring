// Root component — wires the SSE data stream to the UI.
// All data fetching lives in useStockStream; this file is purely layout.
import './App.css'
import { useStockStream } from './hooks/useStockStream'
import Header from './components/Header'
import CompanyTable from './components/CompanyTable'

export default function App() {
  // prices: { [ticker]: { ticker, name, price, change_pct } }
  // news:   array of { title, link, published, source, ticker }
  // connected: true while the SSE connection is open
  const { prices, news, connected, lastUpdated, backendVersion } = useStockStream()

  return (
    <div className="app">
      <Header connected={connected} lastUpdated={lastUpdated} backendVersion={backendVersion} />
      <CompanyTable prices={prices} news={news} />
    </div>
  )
}
