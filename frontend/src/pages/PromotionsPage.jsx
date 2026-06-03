import { useState, useEffect } from 'react'

const API = ''


export default function PromotionsPage() {
  const [promotions, setPromotions] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    setLoading(true)
    fetch(`${API}/api/promotions/`)
      .then(r => r.json())
      .then(d => { setPromotions(d.results); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const filtered = search
    ? promotions.filter(p => p.title.toLowerCase().includes(search.toLowerCase()))
    : promotions

  function handleSearch(e) {
    e.preventDefault()
    setSearch(searchInput)
  }

  return (
    <div className="page">
      <h1 className="page-title">🎁 Акции и скидки</h1>
      <p className="page-subtitle">Актуальные предложения фитнес-клуба</p>

      {/* Поиск */}
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          className="search-input"
          type="text"
          placeholder="Поиск акции..."
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
        />
        <button className="search-btn" type="submit">Найти</button>
        {search && (
          <button className="btn btn-outline" type="button" onClick={() => { setSearch(''); setSearchInput('') }}>✕</button>
        )}
      </form>

      {loading && <div className="loading"><div className="loading-spinner" />Загрузка...</div>}

      {!loading && filtered.length === 0 && (
        <div className="empty-msg">Акций не найдено</div>
      )}

      <div className="cards-grid">
        {filtered.map(p => (
          <div key={p.id} className="promo-card">
            <div className="promo-discount">−{p.discount_percent}%</div>
            <div className="promo-title">{p.title}</div>
            <div className="promo-desc">{p.description}</div>
            <div className="promo-dates">
              {new Date(p.start_date).toLocaleDateString('ru-RU')} –{' '}
              {new Date(p.end_date).toLocaleDateString('ru-RU')}
            </div>
            {p.days_left > 0 && (
              <span className="promo-days-left">⏳ осталось {p.days_left} дн.</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
