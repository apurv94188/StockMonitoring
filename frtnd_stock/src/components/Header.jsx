import './Header.css'

export default function Header({ connected, lastUpdated }) {
  const time = lastUpdated
    ? lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : null

  return (
    <header className="header">
      <div className="header-left">
        <span className="header-title">STOCK MONITOR</span>
      </div>
      <div className="header-right">
        {time && <span className="header-time">updated {time}</span>}
        <span className={`status-dot ${connected ? 'status-live' : 'status-offline'}`} />
        <span className="status-label">{connected ? 'LIVE' : 'OFFLINE'}</span>
      </div>
    </header>
  )
}
