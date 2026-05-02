import './PriceCard.css'

export default function PriceCard({ stock }) {
  const { ticker, name, price, change_pct, current_price_timestamp } = stock
  const hasChange = change_pct != null
  const up = change_pct > 0
  const sign = up ? '+' : ''
  const changeClass = !hasChange ? '' : up ? 'up' : 'down'
  const arrow = up ? '▲' : '▼'
  const timeLabel = current_price_timestamp
    ? new Date(current_price_timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : null

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
      {timeLabel && <div className="card-timestamp">{timeLabel}</div>}
    </div>
  )
}
