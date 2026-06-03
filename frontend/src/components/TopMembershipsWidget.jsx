import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const API = ''

export default function TopMembershipsWidget({ limit = 5, onBuy, buying }) {
  const { user, isClient } = useAuth()
  const navigate = useNavigate()
  const [memberships, setMemberships] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [favorites, setFavorites] = useState(new Set())
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams({ limit, ordering: 'price' })
    if (search) params.set('q', search)
    fetch(`${API}/api/memberships/?${params}`)
      .then(r => { if (!r.ok) throw new Error('Ошибка загрузки'); return r.json() })
      .then(data => { setMemberships(data.results); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [limit, search])

  function handleSearch(e) { e.preventDefault(); setSearch(searchInput) }
  function toggleFavorite(id) {
    setFavorites(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })
  }
  function handleBuyClick(id) {
    if (!user) { navigate('/login'); return }
    if (onBuy) onBuy(id)
  }
  function formatDate(ds) {
    return new Date(ds).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
  }

  return (
    <div className="widget">
      <div className="widget-header">
        <h2 className="widget-title">
          <span className="widget-title-icon">🏆</span>
          Топ-{limit} абонементов
        </h2>
        <Link to="/schedule" className="widget-link">📅 Расписание →</Link>
      </div>

      <form className="search-bar" onSubmit={handleSearch}>
        <input className="search-input" type="text" placeholder="Найти абонемент..."
          value={searchInput} onChange={e => setSearchInput(e.target.value)} />
        <button className="search-btn" type="submit">Найти</button>
        {search && <button className="btn btn-outline" type="button" onClick={() => { setSearch(''); setSearchInput('') }}>✕</button>}
      </form>

      {loading && <div className="loading"><div className="loading-spinner" />Загружаем...</div>}
      {error && <div className="error-msg">⚠️ {error}</div>}
      {!loading && !error && memberships.length === 0 && <div className="empty-msg">Ничего не найдено</div>}

      {!loading && !error && memberships.length > 0 && (
        <ol className="widget-list" style={{ listStyle: 'none' }}>
          {memberships.map((m, idx) => (
            <li key={m.id} className="widget-item">
              <div className="widget-rank">{idx + 1}</div>
              <div className="widget-img-placeholder">🏋️</div>

              <div className="widget-info">
                <Link to="/memberships" className="widget-name">{m.title}</Link>
                <span className="widget-name-en">{m.title_en}</span>
                <div className="widget-meta">
                  <span className="widget-price">{Number(m.price).toLocaleString('ru-RU')} ₽</span>
                  <span>📆 {m.duration_days} дн.</span>
                  {m.visits_limit && <span>🎫 {m.visits_limit} вит.</span>}
                  {m.is_new && <span className="tag tag-green">Новинка</span>}
                </div>
                <div className="widget-date">Добавлен: {formatDate(m.created_at)}</div>
              </div>

              <div className="widget-actions" style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'center' }}>
                {/* Кнопка купить прямо из виджета */}
                {isClient && onBuy && (
                  <button
                    className="btn btn-primary"
                    style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                    onClick={() => handleBuyClick(m.id)}
                    disabled={buying === m.id}
                    title="Купить этот абонемент"
                  >
                    {buying === m.id ? '...' : '🛒'}
                  </button>
                )}
                {!user && onBuy && (
                  <Link to="/login" className="btn btn-outline" style={{ padding: '5px 10px', fontSize: '0.78rem' }}>
                    Войти
                  </Link>
                )}
                {/* Избранное */}
                <button
                  className={`btn-favorite${favorites.has(m.id) ? ' active' : ''}`}
                  title={favorites.has(m.id) ? 'Убрать из избранного' : 'В избранное'}
                  onClick={() => toggleFavorite(m.id)}
                >
                  {favorites.has(m.id) ? '❤️' : '🤍'}
                </button>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
