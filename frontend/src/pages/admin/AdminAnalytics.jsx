import { useState, useEffect } from 'react'

const API = ''

export default function AdminAnalytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/api/admin/analytics/`, { credentials: 'include' })
      .then(r => r.json()).then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="loading-spinner" /></div>
  if (!data) return null

  return (
    <div>
      <h2 className="admin-page-title">📊 Аналитика</h2>

      {/* Агрегация цен */}
      <div className="widget" style={{ marginBottom: 28 }}>
        <h3 style={{ marginBottom: 16, fontSize: '1.1rem', fontWeight: 700 }}>📈 Агрегация данных (AVG, MIN, MAX, SUM)</h3>
        <div className="stats-bar" style={{ marginBottom: 0 }}>
          <div className="stat-box">
            <div className="stat-value">{Number(data.avg_price).toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Средняя цена абонемента</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{Number(data.min_price).toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Мин. цена</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{Number(data.max_price).toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Макс. цена</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{Number(data.total_paid).toLocaleString('ru-RU')} ₽</div>
            <div className="stat-label">Сумма оплаченных заказов</div>
          </div>
        </div>
      </div>

      {/* Статусы заказов */}
      <div className="widget" style={{ marginBottom: 28 }}>
        <h3 style={{ marginBottom: 16, fontSize: '1.1rem', fontWeight: 700 }}>📦 Статистика заказов (COUNT)</h3>
        <div className="stats-bar" style={{ marginBottom: 0 }}>
          <div className="stat-box"><div className="stat-value">{data.total_orders}</div><div className="stat-label">Всего заказов</div></div>
          <div className="stat-box"><div className="stat-value" style={{ color: '#16a34a' }}>{data.paid_orders}</div><div className="stat-label">Оплачено</div></div>
          <div className="stat-box"><div className="stat-value" style={{ color: '#dc2626' }}>{data.cancelled_orders}</div><div className="stat-label">Отменено</div></div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Занятия по услугам */}
        <div className="widget">
          <h3 style={{ marginBottom: 14, fontSize: '1rem', fontWeight: 700 }}>🏋️ Занятий по услугам</h3>
          <table className="admin-table">
            <thead><tr><th>Услуга</th><th>Занятий</th></tr></thead>
            <tbody>
              {data.services_stats.map(s => (
                <tr key={s.id}>
                  <td>{s.title}</td>
                  <td><strong>{s.schedules_count}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Покупки абонементов */}
        <div className="widget">
          <h3 style={{ marginBottom: 14, fontSize: '1rem', fontWeight: 700 }}>💪 Покупки абонементов</h3>
          <table className="admin-table">
            <thead><tr><th>Абонемент</th><th>Цена</th><th>Покупок</th></tr></thead>
            <tbody>
              {data.memberships_stats.map(m => (
                <tr key={m.id}>
                  <td>{m.title}</td>
                  <td>{Number(m.price).toLocaleString('ru-RU')} ₽</td>
                  <td><strong>{m.purchases_count}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Топ пользователей */}
      {data.users_stats.length > 0 && (
        <div className="widget" style={{ marginTop: 24 }}>
          <h3 style={{ marginBottom: 14, fontSize: '1rem', fontWeight: 700 }}>👥 Топ клиентов по заказам</h3>
          <table className="admin-table">
            <thead><tr><th>Клиент</th><th>Email</th><th>Заказов</th><th>Потрачено</th></tr></thead>
            <tbody>
              {data.users_stats.map((u, i) => (
                <tr key={i}>
                  <td><strong>{u.user__full_name}</strong></td>
                  <td style={{ color: '#6b7280', fontSize: '0.85rem' }}>{u.user__email}</td>
                  <td>{u.orders_count}</td>
                  <td style={{ fontWeight: 700, color: '#e85d04' }}>{Number(u.total_spent).toLocaleString('ru-RU')} ₽</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
