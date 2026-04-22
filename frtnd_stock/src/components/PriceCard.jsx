import './PriceCard.css'

export default function PriceCard({ stock }) {
  const { ticker, name, price, change_pct } = stock
  const hasChange = change_pct != null
  const up = change_pct > 0
  const sign = up ? '+' : ''
  const changeClass = !hasChange ? '' : up ? 'up' : 'down'
  const arrow = up ? '▲' : '▼'

  return (
    <div className={`price-card ${hasChange ? changeClass : ''}`}>
      <div className="card-top">
        <span className="card-ticker">{ticker}</span>
        {hasChange && (
          <span className={`card-change ${changeClass}`}>
            {arrow} {sign}{change_pct.toFixed(2)}%
          </span>
        )}
      </div>
      <div className="card-name">{name}</div>
      <div className="card-price">${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
    </div>
  )
}
