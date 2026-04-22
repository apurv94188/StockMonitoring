import PriceCard from './PriceCard'
import './PriceGrid.css'

export default function PriceGrid({ prices }) {
  const entries = Object.values(prices)

  if (!entries.length) {
    return (
      <div className="price-grid-empty">
        <span className="spinner" />
        <span>Fetching prices…</span>
      </div>
    )
  }

  return (
    <div className="price-grid">
      {entries.map((stock) => (
        <PriceCard key={stock.ticker} stock={stock} />
      ))}
    </div>
  )
}
