import './AlertFeed.css'

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function AlertRow({ alert }) {
  const up = alert.change_pct > 0
  const sign = up ? '+' : ''
  const arrow = up ? '▲' : '▼'

  return (
    <div className={`alert-row ${up ? 'up' : 'down'}`}>
      <span className="alert-arrow">{arrow}</span>
      <span className="alert-ticker">{alert.ticker}</span>
      <span className="alert-change">{sign}{alert.change_pct.toFixed(2)}%</span>
      <span className="alert-prices">
        ${alert.previous_price.toFixed(2)} → ${alert.current_price.toFixed(2)}
      </span>
      <span className="alert-time">{formatTime(alert.timestamp)}</span>
    </div>
  )
}

export default function AlertFeed({ alerts }) {
  return (
    <section className="alert-feed">
      <h2 className="section-title">Alerts</h2>
      {alerts.length === 0 ? (
        <p className="section-empty">No alerts yet — watching for threshold breaks…</p>
      ) : (
        <div className="alert-list">
          {alerts.map((a, i) => (
            <AlertRow key={`${a.ticker}-${a.timestamp}-${i}`} alert={a} />
          ))}
        </div>
      )}
    </section>
  )
}
