import './Header.css'
import { FRONTEND_VERSION } from '../version.js'

export default function Header({ connected, lastUpdated, backendVersion }) {
  const time = lastUpdated
    ? lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : null

  return (
    <header className="header">
      <div className="header-left">
        <span className="header-title">STOCK MONITOR</span>
      </div>
      <div className="header-right">
        <span className="header-versions">
          <span className="version-label">FE v{FRONTEND_VERSION}</span>
          <span className="version-sep">·</span>
          <span className="version-label">BE v{backendVersion ?? '—'}</span>
        </span>
        {time && <span className="header-time">updated {time}</span>}
        <span className={`status-dot ${connected ? 'status-live' : 'status-offline'}`} />
        <span className="status-label">{connected ? 'LIVE' : 'OFFLINE'}</span>
      </div>
    </header>
  )
}
