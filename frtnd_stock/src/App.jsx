import './App.css'
import { useStockStream } from './hooks/useStockStream'
import Header from './components/Header'
import CompanyTable from './components/CompanyTable'

export default function App() {
  const { prices, news, connected, lastUpdated } = useStockStream()

  return (
    <div className="app">
      <Header connected={connected} lastUpdated={lastUpdated} />
      <CompanyTable prices={prices} news={news} />
    </div>
  )
}
