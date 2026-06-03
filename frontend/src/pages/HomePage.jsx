import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import TopMembershipsWidget from '../components/TopMembershipsWidget'

const API = ''

export default function HomePage() {
  const { user, isClient } = useAuth()
  const navigate = useNavigate()
  const [promotions, setPromotions] = useState([])
  const [trainers, setTrainers] = useState([])
  const [topByPrice, setTopByPrice] = useState([])
  const [mStats, setMStats] = useState(null)
  const [buyMsg, setBuyMsg] = useState('')
  const [buying, setBuying] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/promotions/`)
      .then(r => r.json()).then(d => setPromotions(d.results.slice(0, 3))).catch(() => {})
    fetch(`${API}/api/trainers/`)
      .then(r => r.json()).then(d => setTrainers(d.results.slice(0, 3))).catch(() => {})
    fetch(`${API}/api/memberships/?limit=5&ordering=-price`)
      .then(r => r.json()).then(d => { setTopByPrice(d.results || []); setMStats(d.stats || null) }).catch(() => {})
  }, [])

  async function handleBuy(id) {
    if (!user) { navigate('/login'); return }
    setBuying(id); setBuyMsg('')
    try {
      const r = await fetch(`${API}/api/memberships/${id}/buy/`, {
        method: 'POST', credentials: 'include',
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error)
      setBuyMsg(`✅ ${data.message}`)
      setTimeout(() => setBuyMsg(''), 4000)
    } catch (e) { setBuyMsg(`❌ ${e.message}`) }
    finally { setBuying(null) }
  }

  return (
    <>
      <div className="hero">
        <div className="hero-inner">
          <h1 className="hero-title">Твой путь к <span>идеальной</span> форме</h1>
          <p className="hero-sub">Профессиональные тренеры, современное оборудование и удобное расписание</p>
          <div className="hero-btns">
            <Link to="/memberships" className="btn btn-primary">🏋️ Выбрать абонемент</Link>
            <Link to="/schedule" className="btn btn-outline" style={{ color: '#fff', borderColor: '#fff' }}>
              📅 Расписание
            </Link>
          </div>
        </div>
      </div>

      <div className="page">
        {buyMsg && (
          <div className={buyMsg.startsWith('✅') ? 'auth-success' : 'auth-error'} style={{ marginBottom: 16 }}>
            {buyMsg}
          </div>
        )}

        {/* Агрегация абонементов — AVG, MIN, MAX, COUNT */}
        {mStats && (
          <div className="stats-bar" style={{ marginBottom: 24 }}>
            <div className="stat-box">
              <div className="stat-value">{mStats.total}</div>
              <div className="stat-label">Всего абонементов</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{Number(mStats.avg_price).toLocaleString('ru-RU')} ₽</div>
              <div className="stat-label">Средняя цена</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{Number(mStats.min_price).toLocaleString('ru-RU')} ₽</div>
              <div className="stat-label">Минимальная цена</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{Number(mStats.max_price).toLocaleString('ru-RU')} ₽</div>
              <div className="stat-label">Максимальная цена</div>
            </div>
          </div>
        )}

        <TopMembershipsWidget limit={5} onBuy={handleBuy} buying={buying} />

        {/* Топ по цене */}
        {topByPrice.length > 0 && (
          <section style={{ marginBottom: 40 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 className="page-title" style={{ marginBottom: 0 }}>💎 Топ по цене</h2>
              <Link to="/memberships" className="widget-link">Все абонементы →</Link>
            </div>
            <div className="widget" style={{ padding: 0, overflow: 'hidden' }}>
              {topByPrice.map((m, idx) => (
                <div key={m.id} style={{
                  display: 'grid',
                  gridTemplateColumns: '40px 1fr auto',
                  alignItems: 'center',
                  gap: 16,
                  padding: '14px 20px',
                  borderBottom: idx < topByPrice.length - 1 ? '1px solid #e5e7eb' : 'none',
                  transition: 'background 0.15s',
                }}
                  onMouseEnter={e => e.currentTarget.style.background = '#fff7ed'}
                  onMouseLeave={e => e.currentTarget.style.background = '#fff'}
                >
                  {/* Позиция */}
                  <div style={{
                    width: 32, height: 32, borderRadius: '50%',
                    background: idx === 0 ? '#ffd700' : idx === 1 ? '#c0c0c0' : idx === 2 ? '#cd7f32' : '#f1f5f9',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 800, fontSize: '0.9rem',
                    color: idx < 3 ? '#fff' : '#6b7280',
                  }}>
                    {idx + 1}
                  </div>

                  {/* Инфо */}
                  <div>
                    <div style={{ fontWeight: 700 }}>{m.title}</div>
                    <div style={{ fontSize: '0.8rem', color: '#9ca3af', fontStyle: 'italic' }}>{m.title_en}</div>
                    <div style={{ fontSize: '0.82rem', color: '#6b7280', marginTop: 2 }}>
                      📆 {m.duration_days} дней
                      {m.visits_limit && ` · 🎫 ${m.visits_limit} визитов`}
                    </div>
                  </div>

                  {/* Цена + кнопка */}
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 900, fontSize: '1.2rem', color: '#e85d04' }}>
                      {Number(m.price).toLocaleString('ru-RU')} ₽
                    </div>
                    {isClient && (
                      <button
                        className="btn btn-primary"
                        style={{ marginTop: 6, padding: '5px 14px', fontSize: '0.82rem' }}
                        onClick={() => handleBuy(m.id)}
                        disabled={buying === m.id}
                      >
                        {buying === m.id ? '...' : '🛒 Купить'}
                      </button>
                    )}
                    {!user && (
                      <Link to="/login" style={{ fontSize: '0.8rem', color: '#e85d04', display: 'block', marginTop: 6 }}>
                        Войти →
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Акции — кликабельные */}
        {promotions.length > 0 && (
          <section style={{ marginBottom: 40 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 className="page-title" style={{ marginBottom: 0 }}>🎁 Актуальные акции</h2>
              <Link to="/promotions" className="widget-link">Все акции →</Link>
            </div>
            <div className="cards-grid">
              {promotions.map(p => (
                <Link key={p.id} to="/promotions" style={{ textDecoration: 'none', display: 'block' }}>
                  <div className="promo-card home-promo-card">
                    <div className="promo-discount">−{p.discount_percent}%</div>
                    <div className="promo-title">{p.title}</div>
                    <div className="promo-desc">{p.description}</div>
                    <div className="promo-dates">до {new Date(p.end_date).toLocaleDateString('ru-RU')}</div>
                    {p.days_left > 0 && <span className="promo-days-left">осталось {p.days_left} дн.</span>}
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Тренеры — ссылка на детальную страницу */}
        {trainers.length > 0 && (
          <section>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 className="page-title" style={{ marginBottom: 0 }}>👨‍🏫 Наши тренеры</h2>
              <Link to="/trainers" className="widget-link">Все тренеры →</Link>
            </div>
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
                      <div className="card-desc">{t.specialization}</div>
                      <div className="card-footer">
                        <span className="tag tag-blue">⭐ {t.experience_years} лет</span>
                        <span style={{ color: '#e85d04', fontSize: '0.85rem', fontWeight: 600 }}>Подробнее →</span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </>
  )
}
