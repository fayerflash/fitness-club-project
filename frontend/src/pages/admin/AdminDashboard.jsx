import { useState, useEffect } from 'react'

const API = ''

export default function AdminDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/admin/dashboard/`, { credentials: 'include' })
      .then(r => r.json()).then(setData).catch(() => {})
  }, [])

  if (!data) return <div className="loading"><div className="loading-spinner" /></div>

  const cards = [
    { icon: '🎫', label: 'Абонементов', value: data.memberships, color: '#e85d04' },
    { icon: '👨‍🏫', label: 'Тренеров', value: data.trainers, color: '#7c3aed' },
    { icon: '🏋️', label: 'Услуг', value: data.services, color: '#0891b2' },
    { icon: '📅', label: 'Занятий (ближ.)', value: data.schedule_upcoming, color: '#059669' },
    { icon: '🎁', label: 'Акций активных', value: data.promotions_active, color: '#d97706' },
    { icon: '👥', label: 'Клиентов', value: data.users, color: '#dc2626' },
    { icon: '📦', label: 'Всего заказов', value: data.orders_total, color: '#6b7280' },
    { icon: '✅', label: 'Оплачено', value: data.orders_paid, color: '#16a34a' },
  ]

  return (
    <div>
      <h2 className="admin-page-title">📊 Дашборд</h2>
      <div className="admin-stats-grid">
        {cards.map(c => (
          <div key={c.label} className="admin-stat-card" style={{ borderTop: `4px solid ${c.color}` }}>
            <div className="admin-stat-icon">{c.icon}</div>
            <div className="admin-stat-value" style={{ color: c.color }}>{c.value}</div>
            <div className="admin-stat-label">{c.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
