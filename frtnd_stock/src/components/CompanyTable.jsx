import './CompanyTable.css'

function timeAgo(published) {
  if (!published) return ''
  const d = new Date(published)
  if (isNaN(d)) return ''
  const diff = Math.floor((Date.now() - d) / 1000)
  if (diff < 60)    return `${diff}s ago`
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function CompanyRow({ stock, news }) {
  const { ticker, name, price, change_pct } = stock
  const hasChange = change_pct != null
  const up = change_pct > 0
  const sign = up ? '+' : ''
  const changeClass = !hasChange ? '' : up ? 'up' : 'down'
  const arrow = up ? '▲' : '▼'

  return (
    <div className={`company-row ${hasChange ? changeClass : ''}`}>
      <div className="col-name">
        <span className="row-ticker">{ticker}</span>
        <span className="row-company-name">{name}</span>
      </div>
      <div className="col-price">
        ${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div className="col-change">
        {hasChange && (
          <span className={changeClass}>
            {arrow} {sign}{change_pct.toFixed(2)}%
          </span>
        )}
      </div>
      <div className="col-news">
        {news.length === 0 ? (
          <span className="no-news">—</span>
        ) : (
          news.map((item, i) => (
            <div key={`${item.link}-${i}`} className="news-sub-row">
              <a href={item.link} target="_blank" rel="noreferrer" className="news-link">
                {item.title}
              </a>
              <span className="news-meta">
                <span className="news-source">{item.source}</span>
                {item.published && <span className="news-age">{timeAgo(item.published)}</span>}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default function CompanyTable({ prices, news }) {
  const entries = Object.values(prices)

  const newsByTicker = {}
  news.forEach(item => {
    if (item.ticker) {
      if (!newsByTicker[item.ticker]) newsByTicker[item.ticker] = []
      newsByTicker[item.ticker].push(item)
    }
  })

  if (!entries.length) {
    return (
      <div className="table-loading">
        <span className="spinner" />
        <span>Fetching prices…</span>
      </div>
    )
  }

  return (
    <div className="company-table">
      <div className="table-header">
        <div className="col-name">Company</div>
        <div className="col-price">Price</div>
        <div className="col-change">Change</div>
        <div className="col-news">News</div>
      </div>
      {entries.map(stock => (
        <CompanyRow
          key={stock.ticker}
          stock={stock}
          news={newsByTicker[stock.ticker] || []}
        />
      ))}
    </div>
  )
}
