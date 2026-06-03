import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API = ''

export default function StatisticsPage() {
  const [trainers, setTrainers] = useState(null)
  const [schedule, setSchedule] = useState(null)
  const [promotions, setPromotions] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/trainers/`).then(r => r.json()),
      fetch(`${API}/api/schedule/`).then(r => r.json()),
      fetch(`${API}/api/promotions/`).then(r => r.json()),
    ]).then(([t, s, p]) => {
      setTrainers(t)
      setSchedule(s)
      setPromotions(p)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="page"><div className="loading"><div className="loading-spinner" /></div></div>

  const tStats = trainers?.stats
  const scheduleItems = schedule?.results || []
  const promoItems = promotions?.results || []

  return (
    <div className="page">
      <h1 className="page-title">📊 Статистика клуба</h1>
      <p className="page-subtitle">Актуальные данные по всем разделам</p>

      {/* Тренеры */}
      <section style={{ marginBottom: 36 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>👨‍🏫 Тренеры</h2>
          <Link to="/trainers" className="widget-link" aria-label="Перейти на страницу тренеров">Перейти →</Link>
        </div>
        <div className="stats-bar">
          <div className="stat-box">
            <div className="stat-value">{tStats?.total ?? '—'}</div>
            <div className="stat-label">Всего тренеров</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{tStats?.avg_experience ?? '—'}</div>
            <div className="stat-label">Средний опыт (лет)</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{tStats?.max_experience ?? '—'}</div>
            <div className="stat-label">Макс. опыт (лет)</div>
          </div>
        </div>

        <div className="widget" style={{ marginTop: 16 }}>
          <h3 style={{ fontWeight: 700, marginBottom: 12 }}>Топ по опыту</h3>
          <table className="admin-table">
            <thead>
              <tr><th>Фото</th><th>ФИО</th><th>Специализация</th><th>Опыт</th></tr>
            </thead>
            <tbody>
              {(trainers?.results || []).slice(0, 5).map(t => (
                <tr key={t.id} style={{ cursor: 'pointer' }}
                  onClick={() => window.location.href = `/trainers/${t.id}`}
                  aria-label={`Перейти к профилю тренера ${t.full_name}`}
                >
                  <td>
                    {(t.photo_file_url || t.photo_url)
                      ? <img src={t.photo_file_url || t.photo_url} style={{ width: 36, height: 36, borderRadius: '50%', objectFit: 'cover' }} alt={t.full_name} />
                      : <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#e8f4ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }} aria-hidden="true">👤</div>
                    }
                  </td>
                  <td>
                    <strong>{t.full_name}</strong>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', fontStyle: 'italic' }}>{t.full_name_en}</div>
                  </td>
                  <td>{t.specialization}</td>
                  <td><span className="tag tag-blue">{t.experience_label}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Расписание */}
      <section style={{ marginBottom: 36 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>📅 Расписание</h2>
          <Link to="/schedule" className="widget-link" aria-label="Перейти на страницу расписания">Перейти →</Link>
        </div>
        <div className="stats-bar">
          <div className="stat-box">
            <div className="stat-value">{scheduleItems.length}</div>
            <div className="stat-label">Ближайших занятий</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">
              {scheduleItems.length > 0
                ? new Date(scheduleItems[0].class_date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
                : '—'}
            </div>
            <div className="stat-label">Ближайшее занятие</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">
              {[...new Set(scheduleItems.map(s => s.trainer.full_name))].length}
            </div>
            <div className="stat-label">Тренеров в расписании</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">
              {[...new Set(scheduleItems.map(s => s.service.title))].length}
            </div>
            <div className="stat-label">Видов занятий</div>
          </div>
        </div>

        <div className="widget" style={{ marginTop: 16 }}>
          <h3 style={{ fontWeight: 700, marginBottom: 12 }}>Ближайшие занятия</h3>
          <table className="admin-table">
            <thead>
              <tr><th>Дата</th><th>Время</th><th>Занятие</th><th>Тренер</th><th>Зал</th></tr>
            </thead>
            <tbody>
              {scheduleItems.slice(0, 5).map(s => (
                <tr key={s.id}>
                  <td>{new Date(s.class_date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}</td>
                  <td style={{ color: '#e85d04', fontWeight: 700 }}>{s.start_time}–{s.end_time}</td>
                  <td>
                    <strong>{s.service.title}</strong>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', fontStyle: 'italic' }}>{s.service.title_en}</div>
                  </td>
                  <td>{s.trainer.full_name}</td>
                  <td><span className="tag tag-blue">{s.hall}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Акции */}
      <section style={{ marginBottom: 36 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>🎁 Акции</h2>
          <Link to="/promotions" className="widget-link" aria-label="Перейти на страницу акций">Перейти →</Link>
        </div>
        <div className="stats-bar">
          <div className="stat-box">
            <div className="stat-value">{promoItems.length}</div>
            <div className="stat-label">Активных акций</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">
              {promoItems.length > 0
                ? `${Math.max(...promoItems.map(p => parseFloat(p.discount_percent)))}%`
                : '—'}
            </div>
            <div className="stat-label">Макс. скидка</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">
              {promoItems.length > 0
                ? `${Math.round(promoItems.reduce((s, p) => s + p.days_left, 0) / promoItems.length)} дн.`
                : '—'}
            </div>
            <div className="stat-label">Ср. дней до конца</div>
          </div>
        </div>

        <div className="cards-grid" style={{ marginTop: 16 }}>
          {promoItems.map(p => (
            <Link key={p.id} to="/promotions" style={{ textDecoration: 'none' }}
              aria-label={`Акция ${p.title} — скидка ${p.discount_percent}%`}
            >
              <div className="promo-card">
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
    </div>
  )
}
