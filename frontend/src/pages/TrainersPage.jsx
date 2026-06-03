import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API = ''


export default function TrainersPage() {
  const [trainers, setTrainers] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (search) params.set('q', search)

    fetch(`${API}/api/trainers/?${params}`)
      .then(r => r.json())
      .then(d => { setTrainers(d.results); setStats(d.stats); setLoading(false) })
      .catch(() => setLoading(false))
  }, [search])

  function handleSearch(e) {
    e.preventDefault()
    setSearch(searchInput)
  }

  return (
    <div className="page">
      <h1 className="page-title">👨‍🏫 Наши тренеры</h1>
      <p className="page-subtitle">Профессионалы своего дела</p>

      {/* Поиск */}
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          className="search-input"
          type="text"
          placeholder="Поиск по имени или специализации..."
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
        />
        <button className="search-btn" type="submit">Найти</button>
        {search && (
          <button className="btn btn-outline" type="button" onClick={() => { setSearch(''); setSearchInput('') }}>✕</button>
        )}
      </form>

      {/* Статистика */}
      {stats && (
        <div className="stats-bar">
          <div className="stat-box">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Тренеров</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.avg_experience}</div>
            <div className="stat-label">Средний опыт (лет)</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.max_experience}</div>
            <div className="stat-label">Макс. опыт (лет)</div>
          </div>
        </div>
      )}

      {loading && <div className="loading"><div className="loading-spinner" />Загрузка...</div>}

      <div className="cards-grid">
        {trainers.map(t => (
          <Link key={t.id} to={`/trainers/${t.id}`} style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer' }}>
              {(t.photo_file_url || t.photo_url)
                ? <img src={t.photo_file_url || t.photo_url} alt={t.full_name} className="card-img" />
                : <div className="card-img-placeholder">👤</div>
              }
              <div className="card-body">
                <div className="card-title">{t.full_name}</div>
                <div className="card-title-en">{t.full_name_en}</div>
                <div className="card-desc">{t.bio || t.specialization}</div>
                <div style={{ marginBottom: 8 }}>
                  {t.specialization.split(', ').map(s => (
                    <span key={s} className="tag tag-orange">{s}</span>
                  ))}
                </div>
                <div className="card-footer">
                  <span className="tag tag-blue">⭐ {t.experience_label}</span>
                  <span style={{ color: '#e85d04', fontWeight: 600, fontSize: '0.85rem' }}>Подробнее →</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!loading && trainers.length === 0 && (
        <div className="empty-msg">Тренеры не найдены</div>
      )}
    </div>
  )
}
