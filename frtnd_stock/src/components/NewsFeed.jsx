import './NewsFeed.css'

function timeAgo(published) {
  if (!published) return ''
  const d = new Date(published)
  if (isNaN(d)) return ''
  const diff = Math.floor((Date.now() - d) / 1000)
  if (diff < 60)   return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function NewsRow({ item }) {
  return (
    <div className="news-row">
      {item.ticker && <span className="news-ticker">{item.ticker}</span>}
      <a className="news-title" href={item.link} target="_blank" rel="noreferrer">
        {item.title}
      </a>
      <span className="news-meta">
        <span className="news-source">{item.source}</span>
        {item.published && <span className="news-age">{timeAgo(item.published)}</span>}
      </span>
    </div>
  )
}

export default function NewsFeed({ news }) {
  return (
    <section className="news-feed">
      <h2 className="section-title">News</h2>
      {news.length === 0 ? (
        <p className="section-empty">News loads every 5 minutes…</p>
      ) : (
        <div className="news-list">
          {news.map((item, i) => (
            <NewsRow key={`${item.link}-${i}`} item={item} />
          ))}
        </div>
      )}
    </section>
  )
}
