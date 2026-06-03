import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const API = ''


export default function MembershipsPage() {
  const { user, isClient } = useAuth()
  const [memberships, setMemberships] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [ordering, setOrdering] = useState('price')
  const [favorites, setFavorites] = useState(new Set())
  const [buying, setBuying] = useState(null)
  const [buyMsg, setBuyMsg] = useState('')

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams({ limit: 20, ordering })
    if (search) params.set('q', search)

    fetch(`${API}/api/memberships/?${params}`)
      .then(r => r.json())
      .then(d => { setMemberships(d.results); setStats(d.stats); setLoading(false) })
      .catch(() => setLoading(false))
  }, [search, ordering])

  function handleSearch(e) {
    e.preventDefault()
    setSearch(searchInput)
  }

  async function handleBuy(id) {
    setBuying(id)
    setBuyMsg('')
    try {
      const r = await fetch(`${API}/api/memberships/${id}/buy/`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error)
      setBuyMsg(`✅ ${data.message}`)
      setTimeout(() => setBuyMsg(''), 4000)
    } catch (err) {
      setBuyMsg(`❌ ${err.message}`)
    } finally {
      setBuying(null)
    }
  }

  function toggleFavorite(id) {
    setFavorites(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <div className="page">
      <h1 className="page-title">🏋️ Абонементы</h1>
      <p className="page-subtitle">Выберите подходящий абонемент</p>

      {/* Поиск */}
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          className="search-input"
          type="text"
          placeholder="Поиск по названию..."
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
        />
        <select
          value={ordering}
          onChange={e => setOrdering(e.target.value)}
          style={{ padding: '12px 14px', borderRadius: 10, border: '2px solid #e5e7eb', background: '#fff', fontSize: '1rem' }}
        >
          <option value="price">По цене ↑</option>
          <option value="-price">По цене ↓</option>
          <option value="-created_at">Новые</option>
          <option value="duration_days">По сроку</option>
        </select>
        <button className="search-btn" type="submit">Найти</button>
        {search && (
          <button className="btn btn-outline" type="button" onClick={() => { setSearch(''); setSearchInput('') }}>✕</button>
        )}
      </form>

      {/* Статистика — агрегатные данные */}
      {stats && (
        <div className="stats-bar">
          <div className="stat-box">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Всего абонементов</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.avg_price?.toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Средняя цена</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{Number(stats.min_price).toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Минимальная цена</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{Number(stats.max_price).toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Максимальная цена</div>
          </div>
        </div>
      )}

      {buyMsg && (
        <div className={buyMsg.startsWith('✅') ? 'auth-success' : 'auth-error'} style={{ marginBottom: 16 }}>
          {buyMsg}
        </div>
      )}

      {loading && <div className="loading"><div className="loading-spinner" />Загрузка...</div>}

      {!loading && memberships.length === 0 && (
        <div className="empty-msg">Абонементы не найдены</div>
      )}

      <div className="cards-grid">
        {memberships.map(m => (
          <div key={m.id} className="card">
            <div className="card-img-placeholder">🏋️</div>
            <div className="card-body">
              <div className="card-title">{m.title}</div>
              <div className="card-title-en">{m.title_en}</div>
              <div className="card-desc">{m.description || 'Нет описания'}</div>
              <div style={{ marginBottom: 8 }}>
                {m.is_new && <span className="tag tag-green">Новинка</span>}
                {m.visits_limit && <span className="tag tag-blue">🎫 {m.visits_limit} визитов</span>}
              </div>
              <div className="card-footer" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                  <div>
                    <div className="card-price">{Number(m.price).toLocaleString('ru-RU')} ₽</div>
                    <div className="card-date">{m.duration_days} дней</div>
                  </div>
                  <button
                    className={`btn-favorite${favorites.has(m.id) ? ' active' : ''}`}
                    title="В избранное"
                    onClick={() => toggleFavorite(m.id)}
                  >
                    {favorites.has(m.id) ? '❤️' : '🤍'}
                  </button>
                </div>
                {isClient && (
                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', justifyContent: 'center' }}
                    onClick={() => handleBuy(m.id)}
                    disabled={buying === m.id}
                  >
                    {buying === m.id ? 'Покупаем...' : '🛒 Купить'}
                  </button>
                )}
                {!user && (
                  <Link to="/login" className="btn btn-outline" style={{ width: '100%', textAlign: 'center', justifyContent: 'center' }}>
                    Войдите чтобы купить
                  </Link>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
